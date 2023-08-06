# ATS
from ats import aetest

from . import _commons_internal

# subsections for common_setup
@aetest.subsection
def connect(self, testbed):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.connect(self, testbed)

@aetest.subsection
def disconnect(self, testbed):
    '''Connect all the devices defined in mapping file'''
    return _commons_internal.disconnect(self, testbed)

@aetest.subsection
def configure(self, testbed):
    '''Configure the devices'''
    return _commons_internal.configure(self, testbed)

@aetest.subsection
def check_config(self, testbed, testscript):
    '''Take snapshot of configuration for each devices'''
    return _commons_internal.check_config(self, testbed, testscript)

@aetest.subsection
def initialize_traffic(self, steps, testbed):

    return _commons_internal.initialize_traffic(self, steps, testbed)

# subsections for common_cleanup
@aetest.subsection
def check_post_config(self, configs, testbed, testscript):
    '''Verify the configuration for the devices has not changed'''
    return _commons_internal.check_post_config(self, configs, testbed, testscript)

# subsections for common_cleanup
@aetest.subsection
def stop_traffic(self, testbed):
    return _commons_internal.stop_traffic(self, testbed)


class ProfileSystem(object):

    @aetest.subsection
    def ProfileSystem(self, feature, container, testscript, testbed):
        return _commons_internal.ProfileSystem.ProfileSystem(self, feature, container, testscript, testbed)
