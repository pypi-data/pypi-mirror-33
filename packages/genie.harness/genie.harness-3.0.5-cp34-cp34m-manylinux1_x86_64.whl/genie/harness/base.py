import time
import logging
import importlib
import copy
import sys

from genie.abstract import Lookup

from genie.ops.base import Base
from genie.ops.base import Context
from genie.utils.diff import Diff
from ats import aetest
from ats.aetest.script import TestScript
from ats.aetest.testcase import Testcase
from ats.aetest.sections import Subsection
from ats.log.utils import banner
from ats.aetest.signals import ResultSignal

import genie.harness


log = logging.getLogger(__name__)

def verify_object(section, name, verf, ret, exclude, device, last):

    # The name should begins with Verify, so remove pre_ and post_
    name = name.replace('pre_', '').replace('post_', '')

    # Check if snapshot exists
    # Then first time see this device
    if device not in verf:
        # Add everything as it didnt exists anyway
        verf[device] = {}
        verf[device][name] = ret
        return

    # Case where device exists, then check if section.name exists
    if name in verf[device]:
        # Then compare
        new = ret
        old = verf[device][name]
        exclude = ['maker', 'callables', 'device'] + exclude

        diff = Diff(old, new, exclude=exclude)
        diff.findDiff()

        if diff.diffs:
            # then there was some diffs

            # Alright as we don't want all future verification to
            # also fail, retake snapshot Only take snapshot if last and parent
            # is testscript
            if last and isinstance(section.parent, TestScript):
                verf[device][name] = new
            section.failed('Found a difference between original snapshot '
                        'and current snapshot\n{d}'.format(d=str(diff)))
    else:
        # Store
        verf[device][name] = ret

class GenieTrigger(Testcase):
    def parse_args(self, argv):
        pass

class Trigger(GenieTrigger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Used to store local verification snapshots
        self.verf = {}

        # Arguments provided at runtime to be used by triggers
        argv = copy.copy(sys.argv[1:])
        try:
            self.parse_args(argv)
        except Exception as e:
            pass

class TestcaseVerification(GenieTrigger):
    pass

# Must return a dict
class TestcaseVerificationCallable(TestcaseVerification):
    @aetest.test
    def verify(self, uut, **kwargs):
        # Get the name
        name = self.uid.split('.')[0]

        if 'iteration' not in kwargs:
            attempt = 1
            interval = 0
        else:
            iteration = kwargs['iteration']
            attempt = kwargs['iteration']['attempt'] \
                       if 'attempt' in iteration else 1
            interval = kwargs['iteration']['interval'] \
                       if 'interval' in iteration else 0
        exclude = kwargs['exclude'] if 'exclude' in kwargs else []
        genie_parameters = kwargs['genie_parameters']\
                           if 'genie_parameters' in kwargs else {}

        parameters = getattr(self.verify, 'parameters', self.parameters)
        parser_kwargs = parameters.get('parser_kwargs', {})
        parser_kwargs = dict(kwargs, **parser_kwargs)

        # Differen than the other as pyATS already have parameters
        if genie_parameters:
            parser_kwargs['parameters'] = genie_parameters

        # Instanciate Ops object, then go learn it
        for c in range(attempt):
            if attempt-1 == c:
                last = True
            else:
                last = False

            if attempt > 1:
                log.info(banner('{n} out of {t} attempt'.format(n=c+1,
                                                                t=attempt)))
            # Instanciate Ops object, then go learn it
            ret = self.child(**parser_kwargs)
            try:
                verify_object(self, name, ret=ret, verf=self.parent.verf,
                              exclude=exclude, device=uut, last=last)
            except ResultSignal as e:
                # No good; so redo
                last_exception = e
                time.sleep(interval)
            else:
                # all good, so break
                break
        else:
            # No break, so no good, re-raise last exception
            raise(last_exception)


class TestcaseVerificationOps(TestcaseVerification):
    @aetest.test
    def verify(self, uut, **kwargs):
        # Get the name
        name = self.uid.split('.')[0]

        if issubclass(self.child, Template) and\
           'cmd' in kwargs:
            cls = kwargs['cmd']['class']

            # If it has a pkg, then it is assume to be for abstraction
            if 'pkg' in kwargs['cmd']:
                pkg = kwargs['cmd']['pkg']
                # Get package name
                pkg_name = pkg.split('.')[-1]
                mod = importlib.import_module(name=pkg)

                # Lookup is cached,  so only the first time will be slow
                # Otherwise it is fast
                lib = Lookup.from_device(uut, packages={pkg_name:mod})
                # Build the class to used to call
                keys = cls.split('.')
                keys.insert(0, pkg_name)
                for key in keys:
                    lib = getattr(lib, key)
            else:
                # Most likely will never reach here as maker was tailored for
                # Metaparser
                # Just a callable,  assuming it has a .parse so just load it up
                module, class_name = cls.rsplit('.', 1)

                # Load the module
                mod = importlib.import_module(module)

                # Find the right class
                try:
                    lib = getattr(mod, class_name)
                except AttributeError as e:
                    raise AttributeError("Couldn't find class '{name}' in "
                                         "'{mod}'".format(name=class_name,
                                                              mod=mod)) from e

            # And finally change cmd for the right class
            kwargs['cmd'] = lib

        if 'iteration' not in kwargs:
            attempt = 1
            interval = 0
        else:
            iteration = kwargs['iteration']
            attempt = kwargs['iteration']['attempt'] \
                       if 'attempt' in iteration else 1
            interval = kwargs['iteration']['interval'] \
                       if 'interval' in iteration else 0
        genie_parameters = kwargs['genie_parameters']\
                           if 'genie_parameters' in kwargs else {}
        exclude = kwargs['exclude'] if 'exclude' in kwargs else []

        parameters = getattr(self.verify, 'parameters', self.parameters)
        parser_kwargs = parameters.get('parser_kwargs', {})
        kwargs.update(parser_kwargs)
        # Different than the other as pyATS already have parameters
        if genie_parameters:
            parser_kwargs.update(genie_parameters)

        # Instanciate Ops object, then go learn it
        for c in range(attempt):
            # Instanciate Ops object, then go learn it
            if attempt-1 == c:
                last = True
            else:
                last = False
            if attempt > 1:
                log.info(banner('{n} out of {t} attempt'.format(n=c+1,
                                                                t=attempt)))
            old_context = uut.context
            if 'context' in kwargs:
                uut.context = kwargs['context']
            try:
                child = self.child(device=uut, **kwargs)
                if 'context' in kwargs:
                    if kwargs['context'] == 'xml':
                        child.context_manager[kwargs['cmd']] = [Context.xml, Context.cli]
                    elif kwargs['context'] == 'yang':
                        child.context_manager[kwargs['cmd']] = [Context.yang, Context.cli]
                child.learn(**parser_kwargs)
            finally:
                # Revert context 
                uut.context = old_context

            try:
                verify_object(self, name, ret=child, verf=self.parent.verf,
                              exclude=exclude, device=uut.name, last=last)
            except ResultSignal as e:
                # No good; so redo
                last_exception = e
                time.sleep(interval)
                continue
            else:
                # all good, so break
                break
        else:
            # No break, so no good, re-raise last exception
            raise(last_exception)


class LocalVerification(Subsection):
    pass


class Template(Base):
    '''Template for quick ops'''

    def __init__(self, cmd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd = cmd

    def learn(self, **kwargs):
        '''Learn feature object'''

        self.add_leaf(cmd=self.cmd,
                      src='[(?P<all>.*)]',
                      dest='name[(?P<all>.*)]')
        self.make(**kwargs)
