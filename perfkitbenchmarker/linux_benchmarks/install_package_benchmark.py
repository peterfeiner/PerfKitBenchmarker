"""Install packages and export as image.

Sample usage:
blaze-bin/cloud/performance/artemis/artemis --benchmarks=install_package
--packages=wget,build_tools,multilib,numactl,hpcc,fortran,mongodb_server,ycsb,
redis_server,netperf,dstat,gluster,pip
--image_name=image --scratch_disk_type=remote_ssd;

Create image with:
gcloud compute images create ubuntu-packages-20160901-2
--source-uri=gs://artemis_images/image.tar.gz
"""

import logging
from perfkitbenchmarker import configs
from perfkitbenchmarker import flags
from perfkitbenchmarker import linux_packages

flags.DEFINE_list('packages', [], 'Install packages.')
flags.DEFINE_boolean('install_pkb', True, 'Install PKB itself.')
flags.DEFINE_list(
    'data_files', ['cpu2006v1.2.tgz'], 'Data files copied to remote vm.')


BENCHMARK_NAME = 'install_package'
BENCHMARK_CONFIG = """
install_package:
  description: >
    Install packages.
  vm_groups:
    default:
      vm_spec:
        <<: *default_single_core
        GCP:
          <<: *default_single_core_gcp
          boot_disk_size: 500
      vm_count: 1
      disk_spec: *default_500_gb"""


def GetConfig(user_config):
  return configs.LoadConfig(BENCHMARK_CONFIG, user_config, BENCHMARK_NAME)


def InstallPkB(vm):
  vm.RemoteCommand(
      'cd /tmp/; rm -rf /tmp/PerfKitBenchmarker; '
      'git clone https://github.com/GoogleCloudPlatform/PerfKitBenchmarker.git')
  vm.RemoteCommand(
      'sudo pip install -r /tmp/PerfKitBenchmarker/requirements.txt')


def Prepare(benchmark_spec):
  """Install all packages.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
      required to run the benchmark.
  """
  vm = benchmark_spec.vms[0]
  for package in flags.FLAGS.packages or linux_packages.PACKAGES.keys():
    logging.info('Installing %s', package)
    vm.Install(package)
  if flags.FLAGS.install_pkb:
    InstallPkB(vm)


def Run(benchmark_spec):
  return []


def Cleanup(benchmark_spec):  # pylint: disable=unused-argument
  """Cleanup the VM to its original state.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that
      is required to run the benchmark.
  """
  pass
