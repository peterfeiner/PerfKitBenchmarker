URL = 'https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.4.25.tar.gz'
TARBALL = 'linux-4.4.25.tar.gz'
UNTAR_DIR = 'linux-4.4.25'


def _Install(vm):
  vm.Install('build_tools')
  vm.Install('wget')
  vm.RemoteCommand('wget {}'.format(URL))


def AptInstall(vm):
  _Install(vm)


def YumInstall(vm):
  _Install(vm)


def Cleanup(vm):
  vm.RemoteCommand('rm -f {}'.format(TARBALL))
