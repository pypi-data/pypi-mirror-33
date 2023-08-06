# -*- coding: utf-8 -*-

__version__ = "1.5.173"

import base64 as _base64
import glob as _glob
import json as _json
import logging as _logging
import os as _os
import re as _re
import subprocess as _subprocess
import sys as _sys
import tarfile as _tarfile
import time as _time
import warnings as _warnings
from datetime import datetime as _datetime
from inspect import getmembers as _getmembers, isfunction as _isfunction
from pprint import pprint as _pprint

import boto3 as _boto3
from botocore.exceptions import ClientError as _ClientError
import fire as _fire
import jinja2 as _jinja2
import kubernetes.client as _kubeclient
import kubernetes.config as _kubeconfig
import requests as _requests

_invalid_input_az_09_regex_pattern = _re.compile('[^a-z0-9]')

_logger = _logging.getLogger()
_logger.setLevel(_logging.WARNING)
_logging.getLogger("urllib3").setLevel(_logging.WARNING)
_logging.getLogger('kubernetes.client.rest').setLevel(_logging.WARNING)

_ch = _logging.StreamHandler(_sys.stdout)
_ch.setLevel(_logging.DEBUG)
_formatter = _logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch.setFormatter(_formatter)
_logger.addHandler(_ch)

_http_mode = False 

_default_model_template_name = 'default'

_model_subdir_name = 'model'

if _sys.version_info.major == 3:
    from urllib3 import disable_warnings as _disable_warnings
    _disable_warnings()

_Dockerfile_template_registry = {
                                 'predict-server': (['docker/predict-server-local-dockerfile.template'], []),
                                 'train-server': (['docker/train-server-local-dockerfile.template'], []),
                                }

_kube_router_deploy_template_registry = {'predict-router-split': (['yaml/predict-deploy.yaml.template'], []),
                                         'predict-router-gpu-split': (['yaml/predict-gpu-deploy.yaml.template'], [])}

_kube_router_ingress_template_registry = {'predict-router-split': (['yaml/predict-ingress.yaml.template'], [])}
_kube_router_svc_template_registry = {'predict-router-split': (['yaml/predict-svc.yaml.template'], [])}
_kube_router_routerules_template_registry = {'predict-router': (['yaml/predict-routerules.yaml.template'], [])}
_kube_router_autoscale_template_registry = {'predict-router-split': (['yaml/predict-autoscale.yaml.template'], [])}

_kube_stream_deploy_template_registry = {'stream': (['yaml/stream-deploy.yaml.template'], [])}
_kube_stream_svc_template_registry = {'stream': (['yaml/stream-svc.yaml.template'], [])}
_kube_stream_ingress_template_registry = {'stream': (['yaml/stream-ingress.yaml.template'], [])}
_kube_stream_routerules_template_registry = {'stream': (['yaml/stream-routerules.yaml.template'], [])}

_train_kube_template_registry = {'train-cluster': (['yaml/train-cluster.yaml.template'], []),
                                 'train-gpu-cluster': (['yaml/train-gpu-cluster.yaml.template'], [])}

_pipeline_api_version = 'v1'

_default_pipeline_templates_path = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), 'templates'))
_default_pipeline_services_path = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), 'services'))

_default_image_registry_url = 'docker.io'
_default_image_registry_repo = 'pipelineai'

_default_ecr_image_registry_url = '954636985443.dkr.ecr.us-west-2.amazonaws.com'
_default_ecr_image_registry_repo = 'pipelineai'

_default_image_registry_train_namespace = 'train'
_default_image_registry_predict_namespace = 'predict'
_default_image_registry_stream_namespace = 'stream'
_default_image_registry_base_tag = '1.5.0'

_default_model_chip = 'cpu'

_default_build_type = 'docker'
_default_build_context_path = '.'

_default_namespace = 'default'

_pipelineai_dockerhub_cpu_image_list = [
    'predict-cpu',
    'ubuntu-16.04-cpu',
    'train-cpu',
    'stream-cpu'
]

# These are always additive to the CPU images ^^
_pipelineai_dockerhub_gpu_image_list = [
    'predict-gpu',
    'ubuntu-16.04-gpu',
    'train-gpu',
    'stream-gpu'
]

_pipelineai_ecr_cpu_image_list = [
    'predict-cpu',
    'ubuntu-16.04-cpu',
    'train-cpu',
    'stream-cpu',
    'notebook-cpu',
    'metastore-2.1.1',
    'dashboard-hystrix',
    'dashboard-turbine',
    'prometheus',
    'grafana',
    'admin',
    'api',
    'mysql-master',
    'redis-master',
    'metastore-2.1.1',
    'hdfs-namenode',
    'spark-2.3.0-base',
    'spark-2.3.0-master',
    'spark-2.3.0-worker',
    'spark-2.3.0-kube',
    'mongo-3.4.13',
    'pipelinedb-backend',
    'node-9.8.0',
    'pipelinedb-frontend',
    'logging-elasticsearch-6.3.0',
    'logging-kibana-oss-6.3.0',
    'logging-fluentd-kubernetes-v1.2.2-debian-elasticsearch'
]

# These are always additive to the CPU images ^^
_pipelineai_ecr_gpu_image_list = [
    'predict-gpu',
    'ubuntu-16.04-gpu',
    'train-gpu',
    'stream-gpu',
    'notebook-gpu'
]

# These are free-form, but could be locked down to 0.7.1
#  However, they work with the _other_image_list below
_istio_image_list = [
    'docker.io/istio/proxy_init:0.7.1',
    'docker.io/istio/proxy:0.7.1',
    'docker.io/istio/istio-ca:0.7.1',
    'docker.io/istio/mixer:0.7.1',
    'docker.io/istio/pilot:0.7.1',
    'docker.io/istio/servicegraph:0.7.1'
]

_vizier_image_list = [
    'docker.io/mysql:8.0.3',
    'docker.io/katib/vizier-core:v0.1.2-alpha',
    'docker.io/katib/earlystopping-medianstopping:v0.1.2-alpha',
    'docker.io/katib/suggestion-bayesianoptimization:v0.1.2-alpha',
    'docker.io/katib/suggestion-grid:v0.1.2-alpha',
    'docker.io/katib/suggestion-hyperband:v0.1.1-alpha',
    'docker.io/katib/suggestion-random:v0.1.2-alpha',
]

_other_image_list = [
    'docker.io/prom/statsd-exporter:v0.5.0',
    'k8s.gcr.io/kubernetes-dashboard-amd64:v1.8.3',
    'gcr.io/google_containers/heapster:v1.4.0',
    'gcr.io/google_containers/addon-resizer:2.0',
    'docker.io/jaegertracing/all-in-one:1.5.0',
    'docker.io/mitdbg/modeldb-frontend:latest',
]


# If no image_registry_url, image_registry_repo, or tag are given,
# we assume that each element in image_list contains all 3, so we just pull it as is
def _sync_registry(image_list,
                   tag=None,
                   image_registry_url=None,
                   image_registry_repo=None):

    if tag and image_registry_url and image_registry_repo:
        for image in image_list:
            cmd = 'docker pull %s/%s/%s:%s' % (image_registry_url, image_registry_repo, image, tag)
            print(cmd)
            print("")
            # TODO:  return check_output
            _subprocess.call(cmd, shell=True)
    else:
        for image in image_list:
            cmd = 'docker pull %s' % image
            print(cmd)
            print("")
            # TODO:  return check_output
            _subprocess.call(cmd, shell=True)


def env_registry_sync(tag,
                      chip=_default_model_chip,
                      image_registry_url=_default_image_registry_url,
                      image_registry_repo=_default_image_registry_repo):

    # Do GPU first because it's more specialized
    if chip == 'gpu':
        _sync_registry(_pipelineai_dockerhub_gpu_image_list,
                       tag,
                       image_registry_url,
                       image_registry_repo)

    _sync_registry(_pipelineai_dockerhub_cpu_image_list,
                   tag,
                   image_registry_url,
                   image_registry_repo)
    # TODO:  Return http/json


def _env_registry_fullsync(tag,
                          chip=_default_model_chip,
                          image_registry_url=_default_image_registry_url,
                          image_registry_repo=_default_image_registry_repo,
                          private_image_registry_url=_default_ecr_image_registry_url,
                          private_image_registry_repo=_default_ecr_image_registry_repo):

    env_registry_sync(tag,
                      chip,
                      image_registry_url,
                      image_registry_repo)

    _sync_registry(_istio_image_list)
    _sync_registry(_vizier_image_list)
    _sync_registry(_other_image_list)

    _sync_registry(_pipelineai_ecr_cpu_image_list,
                   tag,
                   private_image_registry_url,
                   private_image_registry_repo)

    _sync_registry(_pipelineai_ecr_gpu_image_list,
                   tag,
                   private_image_registry_url,
                   private_image_registry_repo)


    # TODO:  warn about not being whitelisted for private repos.  contact@pipeline.ai
    # TODO:  return http/json


def help():
    print("Available commands:")
    this_module = _sys.modules[__name__]
    functions = [o[0] for o in _getmembers(this_module) if _isfunction(o[1])]
    functions = [function.replace('_', '-') for function in functions if not function.startswith('_')]
    functions = sorted(functions)
    print("\n".join(functions))


def version():
    print('')
    print('CLI version: %s' % __version__)
    print('API version: %s' % _pipeline_api_version)
    print('')
    print('Default build type: %s' % _default_build_type)

    build_context_path = _os.path.expandvars(_default_build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)

    print('Default build context path: %s => %s' % (_default_build_context_path, build_context_path))
    print('')
    train_base_image_default = '%s/%s/%s-%s:%s' % (_default_image_registry_url, _default_image_registry_repo, _default_image_registry_train_namespace, _default_model_chip, _default_image_registry_base_tag)
    predict_base_image_default = '%s/%s/%s-%s:%s' % (_default_image_registry_url, _default_image_registry_repo, _default_image_registry_predict_namespace, _default_model_chip, _default_image_registry_base_tag)
    print('Default train base image: %s' % train_base_image_default)
    print('Default predict base image: %s' % predict_base_image_default)
    print('')

    return_dict = {
        "cli_version": __version__,
        "api_version": _pipeline_api_version,
        "build_type_default": _default_build_type,
        "build_context_path": build_context_path,
        "build_context_path_default": _default_build_context_path,
        "train_base_image_default": train_base_image_default,
        "predict_base_image_default": predict_base_image_default
    }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _templates_path():
    print("")
    print("Templates path: %s" % _default_pipeline_templates_path)
    print("")

    return _default_pipeline_templates_path


def _get_default_model_runtime(model_type):
    model_runtime = 'python'

    if model_type in ['keras', 'python', 'scikit', 'pytorch', 'xgboost']:
        model_runtime = 'python'

    if model_type in ['java', 'pmml', 'spark']:
        model_runtime = 'jvm'

    if model_type in ['tensorflow']:
        model_runtime = 'tfserving'

    if model_type in ['caffe', 'cpp']:
        model_runtime = 'cpp'

    if model_type in ['mxnet', 'onnx']:
        model_runtime = 'onnx'

    if model_type in ['javascript', 'tensorflowjs']:
        model_runtime = 'nginx'

    if model_type in ['nodejs']:
        model_runtime = 'nodejs'

    if model_type in ['bash']:
        model_runtime = 'bash'

    return model_runtime


# Make sure model_tag is DNS compliant since this may be used as a DNS hostname.
# We might also want to remove '-' and '_', etc.
def _validate_and_prep_model_tag(model_tag):
    if type(model_tag) != str:
        model_tag = str(model_tag)
    model_tag = model_tag.lower()
    return _invalid_input_az_09_regex_pattern.sub('', model_tag)


# Make sure model_name is DNS compliant since this may be used as a DNS hostname.
# We might also want to remove '-' and '_', etc.
def _validate_and_prep_model_name(model_name):
    if type(model_name) != str:
        model_name = str(model_name)
    model_name = model_name.lower()
    return _invalid_input_az_09_regex_pattern.sub('', model_name)


def _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict):
    model_weight_total = 0
    for tag, _ in model_split_tag_and_weight_dict.items():
        tag = _validate_and_prep_model_tag(tag)
        model_weight = int(model_split_tag_and_weight_dict[tag])
        model_weight_total += model_weight

    if model_weight_total != 100:
        raise ValueError("Total of '%s' for weights '%s' does not equal 100 as expected." % (model_weight_total, model_split_tag_and_weight_dict))

    return


def _safe_get_istio_ingress_nodeport(namespace):
    try:
        istio_ingress_nodeport = _get_istio_ingress_nodeport(namespace)
    except Exception:
        istio_ingress_nodeport = '<ingress-controller-nodeport>'
    return istio_ingress_nodeport


def _safe_get_istio_ingress_ip(namespace):
    try:
        istio_ingress_ip = _get_istio_ingress_ip(namespace)
    except Exception:
        istio_ingress_ip = '<ingress-controller-ip>'
    return istio_ingress_ip


def _get_model_ingress(
    model_name,
    namespace,
    image_registry_namespace
):

    model_name = _validate_and_prep_model_name(model_name)

    host = None
    path = ''
    ingress_name = '%s-%s' % (image_registry_namespace, model_name)

    # handle ingresses.extensions not found error
    # when no ingress has been deployed
    try:
        api_client_configuration = _kubeclient.ApiClient(
            _kubeconfig.load_kube_config()
        )
        kubeclient_extensions_v1_beta1 = _kubeclient.ExtensionsV1beta1Api(
            api_client_configuration
        )

        ingress = kubeclient_extensions_v1_beta1.read_namespaced_ingress(
            name=ingress_name,
            namespace=namespace
        )

        lb = ingress.status.load_balancer.ingress if ingress else None
        lb_ingress = lb[0] if len(lb) > 0 else None

        host = lb_ingress.hostname or lb_ingress.ip if lb_ingress else None

        path = ingress.spec.rules[0].http.paths[0].path

    except Exception as exc:
        print(str(exc))

    if not host:
        host = '%s:%s' % (
            _safe_get_istio_ingress_ip(namespace),
            _safe_get_istio_ingress_nodeport(namespace)
        )

    return ('https://%s%s' % (host, path)).replace(".*", "invoke")


def predict_kube_endpoint(model_name,
                          namespace=None,
                          image_registry_namespace=None):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        endpoint_url = _get_model_kube_endpoint(model_name=model_name,
                                                namespace=namespace,
                                                image_registry_namespace=image_registry_namespace)

        response = kubeclient_v1_beta1.list_namespaced_deployment(namespace=namespace,
                                                                  include_uninitialized=True,
                                                                  watch=False,
                                                                  limit=1000,
                                                                  pretty=False)

        deployments = response.items
        model_variant_list = [deployment.metadata.name for deployment in deployments
                               if '%s-%s' % (image_registry_namespace, model_name) in deployment.metadata.name]

    return_dict = {"endpoint_url": endpoint_url,
                   "model_variants": model_variant_list}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_kube_endpoints(
    namespace=None,
    image_registry_namespace=None
):
    """

    :param namespace:
    :param image_registry_namespace:
    :return:
    """

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    _kubeconfig.load_kube_config()
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")

        endpoint_list = _get_all_model_endpoints(
            namespace=namespace,
            image_registry_namespace=image_registry_namespace
        )

        return_dict = {"endpoints": endpoint_list}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict


def _get_sage_endpoint_url(model_name,
                           model_region,
                           image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    return 'https://runtime.sagemaker.%s.amazonaws.com/endpoints/%s-%s/invocations' % (model_region, image_registry_namespace, model_name)


def predict_kube_connect(model_name,
                         model_tag,
                         local_port=None,
                         service_port=None,
                         namespace=None,
                         image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_connect(service_name=service_name,
                     namespace=namespace,
                     local_port=local_port,
                     service_port=service_port)


def _service_connect(service_name,
                     namespace=None,
                     local_port=None,
                     service_port=None):

    if not namespace:
        namespace = _default_namespace

    pod = _get_pod_by_service_name(service_name=service_name)
    if not pod:
        print("")
        print("Service '%s' is not running." % service_name)
        print("")
        return
    if not service_port:
        svc = _get_svc_by_service_name(service_name=service_name)
        if not svc:
            print("")
            print("Service '%s' proxy port cannot be found." % service_name)
            print("")
            return
        service_port = svc.spec.ports[0].target_port

    if not local_port:
        print("")
        print("Proxying local port '<randomly-chosen>' to app '%s' port '%s' using pod '%s' in namespace '%s'." % (service_port, service_name, pod.metadata.name, namespace))
        print("")
        print("If you break out of this terminal, your proxy session will end.")
        print("")
        print("Use 'http://127.0.0.1:<randomly-chosen>' to access app '%s' on port '%s' in namespace '%s'." % (service_name, service_port, namespace))
        print("")
        cmd = 'kubectl port-forward %s :%s --namespace=%s' % (pod.metadata.name, service_port, namespace)
        print(cmd)
        print("")
    else:
        print("")
        print("Proxying local port '%s' to app '%s' port '%s' using pod '%s' in namespace '%s'." % (local_port, service_port, service_name, pod.metadata.name, namespace))
        print("")
        print("If you break out of this terminal, your proxy session will end.")
        print("")
        print("Use 'http://127.0.0.1:%s' to access app '%s' on port '%s' in namespace '%s'." % (local_port, service_name, service_port, namespace))
        print("")
        cmd = 'kubectl port-forward %s %s:%s --namespace=%s' % (pod.metadata.name, local_port, service_port, namespace)
        print(cmd)
        print("")

    _subprocess.call(cmd, shell=True)
    print("")


def _create_predict_server_Dockerfile(model_name,
                                      model_tag,
                                      model_path,
                                      model_type,
                                      model_runtime,
                                      model_chip,
                                      stream_logger_url,
                                      stream_logger_topic,
                                      stream_input_url,
                                      stream_input_topic,
                                      stream_output_url,
                                      stream_output_topic,
                                      image_registry_url,
                                      image_registry_repo,
                                      image_registry_namespace,
                                      image_registry_base_tag,
                                      image_registry_base_chip,
                                      pipeline_templates_path,
                                      build_context_path):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_PATH': model_path,
               'PIPELINE_MODEL_TYPE': model_type,
               'PIPELINE_MODEL_RUNTIME': model_runtime,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    model_predict_cpu_Dockerfile_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _Dockerfile_template_registry['predict-server'][0][0]))
    path, filename = _os.path.split(model_predict_cpu_Dockerfile_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_Dockerfile = _os.path.normpath('%s/.pipeline-generated-%s-%s-%s-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_name, model_tag, model_type, model_runtime, model_chip))
    with open(rendered_Dockerfile, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_Dockerfile))

    return rendered_Dockerfile


def predict_server_describe(model_name,
                            model_tag,
                            namespace=None,
                            image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    return _service_describe(service_name=service_name,
                             namespace=namespace)


def _is_base64_encoded(data):
    try:
        data = data.encode('utf-8')
    except:
        pass

    try:
        if _base64.b64encode(_base64.b64decode(data)) == data:
            return True
    except:
        pass

    return False


def _decode_base64(data,
                   encoding='utf-8'):
    return _base64.b64decode(data).decode(encoding)


def _encode_base64(data,
                   encoding='utf-8'):
    return _base64.b64encode(data.encode(encoding))


def env_kube_activate(namespace):
    cmd = 'kubectl config set-context $(kubectl config current-context) --namespace=%s' % namespace
    print(cmd)
    _subprocess.call(cmd, shell=True)
    print("")
    cmd = 'kubectl config view | grep namespace'
    print(cmd)
    _subprocess.call(cmd, shell=True)
    print("")


#  Note:  model_path must contain the pipeline_conda_environment.yaml file
def env_conda_activate(model_name,
                       model_tag,
                       model_path='.'):

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    print('Looking for %s/pipeline_conda_environment.yaml' % model_path)

    # TODO:  Check if exists.  If so, warn the user as new packages in pipeline_conda_environment.yaml
    #        will not be picked up after the initial environment creation.
    cmd = 'source activate root && conda env update --name %s-%s -f %s/pipeline_conda_environment.yaml --prune --verbose' % (model_name, model_tag, model_path)
    print(cmd)
    _subprocess.call(cmd, shell=True)
    print("")
    cmd = 'source activate %s-%s' % (model_name, model_tag)
    print(cmd)
    _subprocess.call(cmd, shell=True)
    print("")
    return cmd


# model_name: mnist
# model_tag: gpu
# model_path: tensorflow/mnist-gpu/
# model_type: tensorflow
# model_runtime: tfserving
# model_chip: gpu
#
def predict_server_build(model_name,
                         model_tag,
                         model_type,
                         model_path, # relative to models/ ie. ./tensorflow/mnist/
                         model_runtime=None,
                         model_chip=None,
                         squash=False,
                         no_cache=False,
                         http_proxy=None,
                         https_proxy=None,
                         stream_logger_url=None,
                         stream_logger_topic=None,
                         stream_input_url=None,
                         stream_input_topic=None,
                         stream_output_url=None,
                         stream_output_topic=None,
                         build_type=None,
                         build_context_path=None,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None,
                         image_registry_base_tag=None,
                         image_registry_base_chip=None,
                         pipeline_templates_path=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not build_type:
        build_type = _default_build_type

    if not build_context_path:
        build_context_path = _default_build_context_path

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    build_context_path = _os.path.expandvars(build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    # All these paths must be in the same dir or this won't work - be careful where you start the server or build from.
    pipeline_templates_path = _os.path.relpath(pipeline_templates_path, build_context_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    if _is_base64_encoded(model_path):
        model_path = _decode_base64(model_path)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.normpath(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.relpath(model_path, build_context_path)
    model_path = _os.path.normpath(model_path)

    if build_type == 'docker':
        generated_Dockerfile = _create_predict_server_Dockerfile(model_name=model_name,
                                                                 model_tag=model_tag,
                                                                 model_path=model_path,
                                                                 model_type=model_type,
                                                                 model_runtime=model_runtime,
                                                                 model_chip=model_chip,
                                                                 stream_logger_url=stream_logger_url,
                                                                 stream_logger_topic=stream_logger_topic,
                                                                 stream_input_url=stream_input_url,
                                                                 stream_input_topic=stream_input_topic,
                                                                 stream_output_url=stream_output_url,
                                                                 stream_output_topic=stream_output_topic,
                                                                 image_registry_url=image_registry_url,
                                                                 image_registry_repo=image_registry_repo,
                                                                 image_registry_namespace=image_registry_namespace,
                                                                 image_registry_base_tag=image_registry_base_tag,
                                                                 image_registry_base_chip=image_registry_base_chip,
                                                                 pipeline_templates_path=pipeline_templates_path,
                                                                 build_context_path=build_context_path)

        if http_proxy:
            http_proxy_build_arg_snippet = '--build-arg HTTP_PROXY=%s' % http_proxy
        else:
            http_proxy_build_arg_snippet = ''

        if https_proxy:
            https_proxy_build_arg_snippet = '--build-arg HTTPS_PROXY=%s' % https_proxy
        else:
            https_proxy_build_arg_snippet = ''

        if no_cache:
            no_cache = '--no-cache'
        else:
            no_cache = ''

        if squash:
            squash = '--squash'
        else:
            squash = ''

        print("")
        # TODO: Narrow the build_context_path (difference between model_path and current path?)
        cmd = 'docker build %s %s %s %s -t %s/%s/%s-%s:%s -f %s %s' % (no_cache, squash, http_proxy_build_arg_snippet, https_proxy_build_arg_snippet, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag, generated_Dockerfile, build_context_path)

        print(cmd)
        print("")
        _subprocess.call(cmd, shell=True)
    else:
        return_dict = {"status": "incomplete",
                       "error_message": "Build type '%s' not found" % build_type}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict

    return_dict = {"status": "complete",
                   "cmd": "%s" % cmd,
                   "model_variant": "%s-%s-%s" % (image_registry_namespace, model_name, model_tag),
                   "image": "%s/%s/%s-%s:%s" % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag),
                   "model_path": model_path}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _create_predict_kube_Kubernetes_yaml(model_name,
                                         model_tag,
                                         model_chip=None,
                                         namespace=None,
                                         stream_logger_url=None,
                                         stream_logger_topic=None,
                                         stream_input_url=None,
                                         stream_input_topic=None,
                                         stream_output_url=None,
                                         stream_output_topic=None,
                                         target_core_util_percentage='50',
                                         min_replicas='1',
                                         max_replicas='2',
                                         image_registry_url=None,
                                         image_registry_repo=None,
                                         image_registry_namespace=None,
                                         image_registry_base_tag=None,
                                         image_registry_base_chip=None,
                                         pipeline_templates_path=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not model_chip:
        model_chip = _default_model_chip

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    context = {'PIPELINE_NAMESPACE': namespace,
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_TARGET_CORE_UTIL_PERCENTAGE': target_core_util_percentage,
               'PIPELINE_MIN_REPLICAS': min_replicas,
               'PIPELINE_MAX_REPLICAS': max_replicas,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    rendered_filenames = []

    if model_chip == 'gpu':
        model_router_deploy_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_deploy_template_registry['predict-router-gpu-split'][0][0]))
        path, filename = _os.path.split(model_router_deploy_yaml_templates_path)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-deploy.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'" % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]
    else:
        model_router_deploy_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_deploy_template_registry['predict-router-split'][0][0]))
        path, filename = _os.path.split(model_router_deploy_yaml_templates_path)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-deploy.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'" % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

    model_router_ingress_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_ingress_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_ingress_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-ingress.yaml' % (image_registry_namespace, model_name))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    # routerules template is handled later do not generate it here

    model_router_svc_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_svc_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_svc_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-svc.yaml' % (image_registry_namespace, model_name))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    model_router_autoscale_yaml_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _kube_router_autoscale_template_registry['predict-router-split'][0][0]))
    path, filename = _os.path.split(model_router_autoscale_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-autoscale.yaml' % (image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'" % (filename, rendered_filename))
        rendered_filenames += [rendered_filename]

    return rendered_filenames


def predict_server_shell(model_name,
                         model_tag,
                         image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker exec -it %s bash' % container_name
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def predict_server_register(model_name,
                            model_tag,
                            image_registry_url=None,
                            image_registry_repo=None,
                            image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    registry_type = "docker"
    registry_coordinates = '%s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)

    cmd = 'docker push %s' % registry_coordinates
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "image_registry_url": image_registry_url,
                   "image_registry_repo": image_registry_repo,
                   "image_registry_namespace": image_registry_namespace,
                   "registry_type": registry_type,
                   "registry_coordinates": registry_coordinates
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_server_pull(model_name,
                        model_tag,
                        image_registry_url=None,
                        image_registry_repo=None,
                        image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    cmd = 'docker pull %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def predict_server_start(model_name,
                         model_tag,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None,
                         single_server_only='true',
                         enable_stream_predictions='false',
                         stream_logger_url=None,
                         stream_logger_topic=None,
                         stream_input_url=None,
                         stream_input_topic=None,
                         stream_output_url=None,
                         stream_output_topic=None,
                         predict_port='8080',
                         prometheus_port='9090',
                         grafana_port='3000',
                         memory_limit=None,
                         start_cmd='docker',
                         start_cmd_extra_args=''):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    if not stream_logger_topic:
        stream_logger_topic = '%s-%s-logger' % (model_name, model_tag)

    if not stream_input_topic:
        stream_input_topic = '%s-%s-input' % (model_name, model_tag)

    if not stream_output_topic:
        stream_output_topic = '%s-%s-output' % (model_name, model_tag)

    # Trying to avoid this:
    #   WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap.
    #
    # https://docs.docker.com/config/containers/resource_constraints/#limit-a-containers-access-to-memory
    #
    if not memory_limit:
        memory_limit = ''
    else:
        memory_limit = '--memory=%s --memory-swap=%s' % (memory_limit, memory_limit)

    # Note: We added `serve` to mimic AWS SageMaker and encourage ENTRYPOINT vs CMD as detailed here:
    #       https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html
    cmd = '%s run -itd -p %s:8080 -p %s:9090 -p %s:3000 -e PIPELINE_SINGLE_SERVER_ONLY=%s -e PIPELINE_ENABLE_STREAM_PREDICTIONS=%s -e PIPELINE_STREAM_LOGGER_URL=%s -e PIPELINE_STREAM_LOGGER_TOPIC=%s -e PIPELINE_STREAM_INPUT_URL=%s -e PIPELINE_STREAM_INPUT_TOPIC=%s -e PIPELINE_STREAM_OUTPUT_URL=%s -e PIPELINE_STREAM_OUTPUT_TOPIC=%s --name=%s %s %s %s/%s/%s-%s:%s serve' % (start_cmd, predict_port, prometheus_port, grafana_port, single_server_only, enable_stream_predictions, stream_logger_url, stream_logger_topic, stream_input_url, stream_input_topic, stream_output_url, stream_output_topic, container_name, memory_limit, start_cmd_extra_args, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print("")
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")
    print("==> IGNORE ANY 'WARNING' ABOVE.  IT'S WORKING OK!!")
    print("")
    print("Container start: %s" % container_name)
    print("")
    print("==> Use 'pipeline predict-server-logs --model-name=%s --model-tag=%s' to see logs." % (model_name, model_tag))
    print("")


def predict_server_stop(model_name,
                        model_tag,
                        image_registry_namespace=None,
                        stop_cmd='docker'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    print("")
    cmd = '%s rm -f %s' % (stop_cmd, container_name)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def predict_server_logs(model_name,
                        model_tag,
                        image_registry_namespace=None,
                        logs_cmd='docker'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    print("")
    cmd = '%s logs -f %s' % (logs_cmd, container_name)
    print(cmd)
    print("")

    _subprocess.call(cmd, shell=True)


def _filter_tar(tarinfo):
    ignore_list = []
    for ignore in ignore_list:
        if ignore in tarinfo.name:
            return None

    return tarinfo


def predict_server_tar(model_name,
                       model_tag,
                       model_path,
                       tar_path='.',
                       filemode='w',
                       compression='gz'):

    return model_archive_tar(model_name=model_name,
                             model_tag=model_tag,
                             model_path=model_path,
                             tar_path=tar_path,
                             filemode=filemode,
                             compression=compression)


def model_archive_tar(model_name,
                      model_tag,
                      model_path,
                      tar_path='.',
                      filemode='w',
                      compression='gz'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    tar_path = _os.path.expandvars(tar_path)
    tar_path = _os.path.expanduser(tar_path)
    tar_path = _os.path.abspath(tar_path)
    tar_path = _os.path.normpath(tar_path)

    tar_filename = '%s-%s.tar.gz' % (model_name, model_tag)
    tar_path = _os.path.join(tar_path, tar_filename)

    print("")
    print("Compressing model_path '%s' into tar_path '%s' using '%s' as root dir within the archive." % (model_path, tar_path, _model_subdir_name))

    with _tarfile.open(tar_path, '%s:%s' % (filemode, compression)) as tar:
        tar.add(model_path, arcname=_model_subdir_name, filter=_filter_tar)
        # tar.list()

    return tar_path


def predict_server_untar(model_name,
                         model_tag,
                         model_path,
                         untar_path='.',
                         untar_filename=None,
                         filemode='w',
                         compression='gz'):

    return model_archive_untar(model_name=model_name,
                               model_tag=model_tag,
                               model_path=model_path,
                               untar_path=untar_path,
                               untar_filename=untar_filename,
                               filemode=filemode,
                               compression=compression)


def model_archive_untar(model_name,
                        model_tag,
                        model_path,
                        untar_path='.',
                        untar_filename=None,
                        filemode='r',
                        compression='gz'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)

    untar_path = _os.path.expandvars(untar_path)
    untar_path = _os.path.expanduser(untar_path)
    untar_path = _os.path.abspath(untar_path)
    untar_path = _os.path.normpath(untar_path)

    #print("Untar_path: %s" % untar_path)
    if not untar_filename:
        untar_filename = '%s-%s.tar.gz' % (model_name, model_tag)

    full_untar_path = _os.path.join(untar_path, untar_filename)

    with _tarfile.open(full_untar_path, '%s:%s' % (filemode, compression)) as tar:
        tar.extractall(model_path)

    return untar_path


from werkzeug.utils import secure_filename as _secure_filename
# TODO:  LOCK THIS DOWN TO '.tar.gz'
_ALLOWED_EXTENSIONS = set(['tar', 'gz', 'tar.gz'])


def predict_kube_start(model_name,
                       model_tag,
                       model_chip=None,
                       namespace=None,
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       target_core_util_percentage='50',
                       min_replicas='1',
                       max_replicas='2',
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       image_registry_base_chip=None,
                       pipeline_templates_path=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not model_chip:
        model_chip = _default_model_chip

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    rendered_yamls = _create_predict_kube_Kubernetes_yaml(
                                      model_name=model_name,
                                      model_tag=model_tag,
                                      model_chip=model_chip,
                                      namespace=namespace,
                                      stream_logger_url=stream_logger_url,
                                      stream_logger_topic=stream_logger_topic,
                                      stream_input_url=stream_input_url,
                                      stream_input_topic=stream_input_topic,
                                      stream_output_url=stream_output_url,
                                      stream_output_topic=stream_output_topic,
                                      target_core_util_percentage=target_core_util_percentage,
                                      min_replicas=min_replicas,
                                      max_replicas=max_replicas,
                                      image_registry_url=image_registry_url,
                                      image_registry_repo=image_registry_repo,
                                      image_registry_namespace=image_registry_namespace,
                                      image_registry_base_tag=image_registry_base_tag,
                                      image_registry_base_chip=image_registry_base_chip,
                                      pipeline_templates_path=pipeline_templates_path)

    for rendered_yaml in rendered_yamls:
        # For now, only handle '-deploy' and '-svc' and '-ingress' (not autoscale or routerules)
        if ('-stream-deploy' not in rendered_yaml and '-stream-svc' not in rendered_yaml) and ('-deploy' in rendered_yaml or '-svc' in rendered_yaml or '-ingress' in rendered_yaml):
            _istio_apply(yaml_path=rendered_yaml,
                         namespace=namespace)

    endpoint_url = _get_model_kube_endpoint(model_name=model_name,
                                            namespace=namespace,
                                            image_registry_namespace=image_registry_namespace)

    endpoint_url = endpoint_url.rstrip('/')

    return_dict = {
        "status": "complete",
        "model_name": model_name,
        "model_tag": model_tag,
        "endpoint_url": endpoint_url,
        "comments": "The `endpoint_url` is an internal IP to the ingress controller. No traffic will be allowed until you enable traffic to this endpoint using `pipeline predict-kube-route`. This extra routing step is intentional."
    }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


    response = _requests.get(url=endpoint_url,
                             headers=accept_headers,
                             timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)

    # Consume messages from topic
    endpoint_url = '%s/consumers/%s/instances/%s/records' % (stream_url, stream_consumer_name, stream_consumer_name)
    print(endpoint_url)
    response = _requests.get(url=endpoint_url,
                             headers=accept_headers,
                             timeout=timeout_seconds)

    messages = response.text

    if response.text:
        print("")
        _pprint(response.text)

    # Remove consumer subscription from topic
    endpoint_url = '%s/consumers/%s/instances/%s' % (stream_url, stream_consumer_name, stream_consumer_name)
    endpoint_url = endpoint_url.rstrip('/')
    print(endpoint_url)
    response = _requests.delete(url=endpoint_url,
                                headers=content_type_headers,
                                timeout=timeout_seconds)

    if response.text:
        print("")
        _pprint(response.text)

    return messages


def stream_kube_consume(model_name,
                        model_tag,
                        stream_topic,
                        stream_consumer_name=None,
                        stream_offset=None,
                        namespace=None,
                        image_registry_namespace=None,
                        timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not stream_offset:
        stream_offset = "earliest"

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)
    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = stream_url.rstrip('/')

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    if not stream_consumer_name:
        stream_consumer_name = '%s-%s-%s' % (model_name, model_tag, stream_topic)

    stream_http_consume(stream_url=stream_url,
                        stream_topic=stream_topic,
                        stream_consumer_name=stream_consumer_name,
                        stream_offset=stream_offset,
                        namespace=namespace,
                        image_registry_namespace=image_registry_namespace,
                        timeout_seconds=timeout_seconds)


def predict_stream_test(model_name,
                        model_tag,
                        test_request_path,
                        stream_input_topic=None,
                        namespace=None,
                        image_registry_namespace=None,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    stream_kube_produce(model_name=model_name,
                        model_tag=model_tag,
                        test_request_path=test_request_path,
                        stream_input_topic=stream_input_topic,
                        namespace=namespace,
                        image_registry_namespace=image_registry_namespace,
                        test_request_concurrency=test_request_concurrency,
                        test_request_mime_type=test_request_mime_type,
                        test_response_mime_type=test_response_mime_type,
                        test_request_timeout_seconds=test_request_timeout_seconds)


def stream_http_produce(endpoint_url,
                        test_request_path,
                        test_request_concurrency=1,
                        test_request_timeout_seconds=1200):

    endpoint_url = endpoint_url.rstrip('/')

    print("")
    print("Producing messages for endpoint_url '%s'." % endpoint_url)
    print("")

    accept_and_content_type_headers = {"Accept": "application/vnd.kafka.v2+json", "Content-Type": "application/vnd.kafka.json.v2+json"}

    with open(test_request_path, 'rt') as fh:
        model_input_text = fh.read()

    body = '{"records": [{"value":%s}]}' % model_input_text

    response = _requests.post(url=endpoint_url,
                              headers=accept_and_content_type_headers,
                              data=body.encode('utf-8'),
                              timeout=test_request_timeout_seconds)

    return_dict = {"status": "complete",
                   "endpoint_url": endpoint_url,
                   "headers": accept_and_content_type_headers,
                   "timeout": test_request_timeout_seconds,
                   "test_request_path": test_request_path,
                   "test_request_concurrency": test_request_concurrency,
                   "body": body,
                   "response": response,
                  }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def stream_kube_produce(model_name,
                        model_tag,
                        test_request_path,
                        stream_topic=None,
                        namespace=None,
                        image_registry_namespace=None,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_stream_namespace

    if not stream_topic:
        stream_topic = '%s-%s-input' % (model_name, model_tag)

    service_name = "%s-%s-%s" % (image_registry_namespace, model_name, model_tag)

    stream_url = _get_cluster_service(service_name=service_name,
                                      namespace=namespace)

    stream_url = stream_url.rstrip('/')

    stream_url = 'http://%s/stream/%s/%s' % (stream_url, model_name, model_tag)

    stream_url = stream_url.rstrip('/')

    endpoint_url = '%s/topics/%s' % (stream_url, stream_topic)

    endpoint_url = endpoint_url.rstrip('/')

    # TODO: Enrich return_dict with model_name and model_tag and stream_url and stream_topic
    # TODO:  The following method returns json.
    #        Enrich this json response with `model_name`, `model_tag`, `stream_url`, and `stream_topic`
    return stream_http_produce(endpoint_url=endpoint_url,
                               test_request_path=test_request_path,
                               test_request_concurrency=test_request_concurrency,
                               test_request_mime_type=test_request_mime_type,
                               test_response_mime_type=test_response_mime_type,
                               test_request_timeout_seconds=test_request_timeout_seconds)


# def _optimize_predict(model_name,
#                       model_tag,
#                       model_type,
#                       model_runtime,
#                       model_chip,
#                       model_path,
#                       input_host_path,
#                       output_host_path,
#                       optimize_type,
#                       optimize_params):
#
#     model_name = _validate_and_prep_model_name(model_name)
#     model_tag = _validate_and_prep_model_tag(model_tag)
#
#     model_path = _os.path.expandvars(model_path)
#     model_path = _os.path.expanduser(model_path)
#     model_path = _os.path.abspath(model_path)
#     model_path = _os.path.normpath(model_path)
#
#
# def _optimize_train(
#              model_name,
#              model_tag,
#              model_type,
#              model_runtime,
#              model_chip,
#              model_path,
#              input_host_path,
#              output_host_path,
#              optimize_type,
#              optimize_params):
#
#     model_name = _validate_and_prep_model_name(model_name)
#     model_tag = _validate_and_prep_model_tag(model_tag)
#
#     model_path = _os.path.expandvars(model_path)
#     model_path = _os.path.expanduser(model_path)
#     model_path = _os.path.abspath(model_path)
#     model_path = _os.path.normpath(model_path)


def predict_server_test(endpoint_url,
                        test_request_path,
                        test_request_concurrency=1,
                        test_request_mime_type='application/json',
                        test_response_mime_type='application/json',
                        test_request_timeout_seconds=1200):

    from concurrent.futures import ThreadPoolExecutor

    endpoint_url = endpoint_url.rstrip('/')

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))


def predict_kube_test(model_name,
                      test_request_path,
                      image_registry_namespace=None,
                      namespace=None,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if _is_base64_encoded(test_request_path):
        test_request_path = _decode_base64(test_request_path)

    endpoint_url = _get_model_kube_endpoint(model_name=model_name,
                                            namespace=namespace,
                                            image_registry_namespace=image_registry_namespace)

    endpoint_url = endpoint_url.rstrip('/')

    # This is required to get around the limitation of istio managing only 1 load balancer
    # See here for more details: https://github.com/istio/istio/issues/1752
    # If this gets fixed, we can relax the -routerules.yaml and -ingress.yaml in the templates dir
    #   (we'll no longer need to scope by model_name)

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))
    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "endpoint_url": endpoint_url,
                   "test_request_path": test_request_path,
                   "test_request_concurrency": test_request_concurrency}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_http_test(endpoint_url,
                      test_request_path,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    from concurrent.futures import ThreadPoolExecutor

    endpoint_url = endpoint_url.rstrip('/')

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_predict_http_test(endpoint_url=endpoint_url,
                                               test_request_path=test_request_path,
                                               test_request_mime_type=test_request_mime_type,
                                               test_response_mime_type=test_response_mime_type,
                                               test_request_timeout_seconds=test_request_timeout_seconds))


def _predict_http_test(endpoint_url,
                       test_request_path,
                       test_request_mime_type='application/json',
                       test_response_mime_type='application/json',
                       test_request_timeout_seconds=1200):

    test_request_path = _os.path.expandvars(test_request_path)
    test_request_path = _os.path.expanduser(test_request_path)
    test_request_path = _os.path.abspath(test_request_path)
    test_request_path = _os.path.normpath(test_request_path)

    full_endpoint_url = endpoint_url.rstrip('/')
    print("")
    print("Predicting with file '%s' using '%s'" % (test_request_path, full_endpoint_url))
    print("")

    with open(test_request_path, 'rb') as fh:
        model_input_binary = fh.read()

    headers = {'Content-type': test_request_mime_type, 'Accept': test_response_mime_type}

    begin_time = _datetime.now()
    response = _requests.post(url=full_endpoint_url,
                              headers=headers,
                              data=model_input_binary,
                              timeout=test_request_timeout_seconds)
    end_time = _datetime.now()

    if response.text:
        print("")
        _pprint(response.text)

    print("Status: %s" % response.status_code)

    total_time = end_time - begin_time
    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return_dict = {"status": "complete",
                   "endpoint_url": full_endpoint_url,
                   "test_request_path": test_request_path}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_sage_test(model_name,
                      test_request_path,
                      image_registry_namespace=None,
                      test_request_concurrency=1,
                      test_request_mime_type='application/json',
                      test_response_mime_type='application/json',
                      test_request_timeout_seconds=1200):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
        for _ in range(test_request_concurrency):
            executor.submit(_test_single_prediction_sage(
                                          model_name=model_name,
                                          test_request_path=test_request_path,
                                          image_registry_namespace=image_registry_namespace,
                                          test_request_mime_type=test_request_mime_type,
                                          test_response_mime_type=test_response_mime_type,
                                          test_request_timeout_seconds=test_request_timeout_seconds))


def _test_single_prediction_sage(model_name,
                                 test_request_path,
                                 image_registry_namespace,
                                 test_request_mime_type='application/json',
                                 test_response_mime_type='application/json'):

    test_request_path = _os.path.expandvars(test_request_path)
    test_request_path = _os.path.expanduser(test_request_path)
    test_request_path = _os.path.abspath(test_request_path)
    test_request_path = _os.path.normpath(test_request_path)

    print("")
    print("Predicting with file '%s' using endpoint '%s-%s'" % (test_request_path, image_registry_namespace, model_name))

    with open(test_request_path, 'rb') as fh:
        model_input_binary = fh.read()

    begin_time = _datetime.now()
    body = model_input_binary.decode('utf-8')
    print("Sending body: %s" % body)
    sagemaker_client = _boto3.client('runtime.sagemaker')
    response = sagemaker_client.invoke_endpoint(
                                          EndpointName='%s-%s' % (image_registry_namespace, model_name),
                                          Body=model_input_binary,
                                          ContentType=test_request_mime_type,
                                          Accept=test_response_mime_type)
    end_time = _datetime.now()

    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        print("Variant: '%s'" % response['InvokedProductionVariant'])
        print("")
        _pprint(response['Body'].read().decode('utf-8'))

        print("")
    else:
        return

    total_time = end_time - begin_time
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")


def predict_sage_stop(model_name,
                      image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    sagemaker_client = _boto3.client('sagemaker')

    # Remove Endpoint
    try:
        begin_time = _datetime.now()
        sagemaker_client.delete_endpoint(EndpointName='%s-%s' % (image_registry_namespace, model_name))
        end_time = _datetime.now()
        total_time = end_time - begin_time
        print("Time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")
    except _ClientError:
        pass

    print("Stopped endpoint: %s-%s" % (image_registry_namespace, model_name))

    # Remove Endpoint Config
    try:
        begin_time = _datetime.now()
        sagemaker_client.delete_endpoint_config(EndpointConfigName='%s-%s' % (image_registry_namespace, model_name))
        end_time = _datetime.now()

        total_time = end_time - begin_time
        print("Time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")
    except _ClientError:
        pass

    print("Stopped endpoint config: %s-%s" % (image_registry_namespace, model_name))
    print("")


def predict_sage_describe(model_name,
                          image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    begin_time = _datetime.now()
    sagemaker_client = _boto3.client('sagemaker')
    response = sagemaker_client.describe_endpoint(EndpointName='%s-%s' % (image_registry_namespace, model_name))
    end_time = _datetime.now()

    total_time = end_time - begin_time
    model_region = 'UNKNOWN_REGION'
    print("")
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        status = response['EndpointStatus']
        print("Endpoint Status: '%s'" % status)

        endpoint_arn = response['EndpointArn']
        print("")
        print("EndpointArn: '%s'" % endpoint_arn)
        model_region = endpoint_arn.split(':')[3]
        endpoint_url = _get_sage_endpoint_url(model_name=model_name,
                                              model_region=model_region,
                                              image_registry_namespace=image_registry_namespace)
        print("Endpoint Url: '%s'" % endpoint_url)
        print("")
        print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")


def _get_pod_by_service_name(service_name):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    found = False
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                found = True
                break
    if found:
        return pod
    else:
        return None


def _get_svc_by_service_name(service_name):

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    found = False
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False,
                                                                 pretty=True)
        services = response.items
        for svc in services:
            if service_name in svc.metadata.name:
                found = True
                break
    if found:
        return svc
    else:
        return None


def predict_kube_shell(model_name,
                       model_tag,
                       namespace=None,
                       image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    container_name = '%s-%s' % (image_registry_namespace, model_name)

    _service_shell(service_name=service_name,
                   container_name=container_name,
                   namespace=namespace)


def _service_shell(service_name,
                   container_name=None,
                   namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False,
                                                             pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                break
        print("")
        print("Connecting to '%s'" % pod.metadata.name)
        print("")

        if container_name:
            cmd = "kubectl exec -it %s -c %s bash" % (pod.metadata.name, container_name)
        else:
            cmd = "kubectl exec -it %s bash" % pod.metadata.name

        _subprocess.call(cmd, shell=True)

        print("")


def predict_kube_logs(model_name,
                      model_tag,
                      namespace=None,
                      image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    container_name = '%s-%s' % (image_registry_namespace, model_name)

    _service_logs(service_name=service_name,
                  container_name=container_name,
                  namespace=namespace)


def _service_logs(service_name,
                  container_name=None,
                  namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False,
                                                             pretty=True)
        found = False
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Tailing logs on '%s'." % pod.metadata.name)
            print("")
            if container_name:
                cmd = "kubectl logs -f %s -c %s --namespace=%s" % (pod.metadata.name, container_name, namespace)
            else:
                cmd = "kubectl logs -f %s --namespace=%s" % (pod.metadata.name, namespace)
            print(cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _service_describe(service_name,
                      namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1.list_pod_for_all_namespaces(watch=False,
                                                             pretty=True)
        pods = response.items
        for pod in pods:
            if service_name in pod.metadata.name:
                break
        print("")
        print("Connecting to '%s'" % pod.metadata.name)
        print("")
        cmd = "kubectl get pod %s --namespace=%s -o json" % (pod.metadata.name, namespace)
        service_describe_bytes = _subprocess.check_output(cmd, shell=True)

        return service_describe_bytes.decode('utf-8')


def predict_kube_scale(model_name,
                       model_tag,
                       replicas,
                       namespace=None,
                       image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_scale(service_name=service_name,
                   replicas=replicas,
                   namespace=namespace)

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "replicas": replicas}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_kube_autoscale(model_name,
                           model_tag,
                           cpu_percent,
                           min_replicas,
                           max_replicas,
                           namespace=None,
                           image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    # TODO:  make sure resources/requests/cpu has been set to something in the yaml
    #        ie. istioctl kube-inject -f helloworld.yaml -o helloworld-istio.yaml
    #        then manually edit as follows:
    #
    #  resources:
    #    limits:
    #      cpu: 1000m
    #    requests:
    #      cpu: 100m

    cmd = "kubectl autoscale deployment %s-%s-%s --cpu-percent=%s --min=%s --max=%s --namespace=%s" % (image_registry_namespace, model_name, model_tag, cpu_percent, min_replicas, max_replicas, namespace)
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    cmd = "kubectl get hpa"
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag,
                   "cpu_percent": cpu_percent,
                   "min_replcias": min_replicas,
                   "max_replicas": max_replicas}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def predict_kube_describe(model_name,
                          model_tag,
                          namespace=None,
                          image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    return _service_describe(service_name=service_name,
                             namespace=namespace)


def _service_scale(service_name,
                   replicas,
                   namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    # TODO:  Filter by given `namespace`
    #        I believe there is a new method list_deployment_for_namespace() or some such
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                          pretty=True)
        found = False
        deployments = response.items
        for deploy in deployments:
            if service_name in deploy.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Scaling service '%s' to '%s' replicas." % (deploy.metadata.name, replicas))
            print("")
            cmd = "kubectl scale deploy %s --replicas=%s --namespace=%s" % (deploy.metadata.name, replicas, namespace)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Service '%s' is not running." % service_name)
            print("")


def _kube_apply(yaml_path,
                namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "kubectl apply --namespace %s -f %s" % (namespace, yaml_path)
    _kube(cmd=cmd)


def _kube_create(yaml_path,
                 namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "kubectl create --namespace %s -f %s --save-config --record" % (namespace, yaml_path)
    _kube(cmd=cmd)


def _kube_delete(yaml_path,
                 namespace=None):

    yaml_path = _os.path.normpath(yaml_path)

    if not namespace:
        namespace = _default_namespace

    cmd = "kubectl delete --namespace %s -f %s" % (namespace, yaml_path)
    _kube(cmd=cmd)


def _kube( cmd):
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")


def _predict_kube_routes(
    model_name=None,
    namespace=None,
    image_registry_namespace=None
):

    route_context = ''
    if model_name:
        if not image_registry_namespace:
            image_registry_namespace = _default_image_registry_predict_namespace
        route_context = '%s-%s' % (image_registry_namespace, model_name)

    if not namespace:
        namespace = _default_namespace

    route_dict = dict()
    status = "incomplete"
    cmd = "kubectl get routerule %s-invoke --namespace=%s -o json" % (route_context, namespace)

    try:

        routes = _subprocess.check_output(cmd, shell=True)
        spec = _json.loads(routes.decode('utf-8'))['spec']

        for route in spec.get('route', []):
            route_dict[route['labels']['tag']] = {
                'split': route['weight'],
                'shadow': True if (spec.get('mirror', None) and route['labels']['tag'] in spec['mirror']['labels']['tag']) else False
            }
        status = "complete"
    except Exception as exc:
        print(str(exc))

    return_dict = {
        "status": status,
        "routes": route_dict
    }

    return return_dict


def _get_model_kube_endpoint(model_name,
                             namespace,
                             image_registry_namespace):

    _kubeconfig.load_kube_config()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    ingress_name = '%s-%s' % (image_registry_namespace, model_name)
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        ingress = kubeclient_v1_beta1.read_namespaced_ingress(name=ingress_name,
                                                              namespace=namespace)

        endpoint = None
        if ingress.status.load_balancer.ingress and len(ingress.status.load_balancer.ingress) > 0:
            if (ingress.status.load_balancer.ingress[0].hostname):
                endpoint = ingress.status.load_balancer.ingress[0].hostname
            if (ingress.status.load_balancer.ingress[0].ip):
                endpoint = ingress.status.load_balancer.ingress[0].ip

        if not endpoint:
            try:
                istio_ingress_nodeport = _get_istio_ingress_nodeport(namespace)
            except Exception:
                istio_ingress_nodeport = '<ingress-controller-nodeport>'

            try:
                istio_ingress_ip = _get_istio_ingress_ip(namespace)
            except Exception:
                istio_ingress_ip = '<ingress-controller-ip>'

            endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

        path = ingress.spec.rules[0].http.paths[0].path

        endpoint = 'http://%s%s' % (endpoint, path)
        endpoint = endpoint.replace(".*", "invoke")

        return endpoint


def _get_istio_ingress_nodeport(namespace):
    cmd = "kubectl get svc -n %s istio-ingress -o jsonpath='{.spec.ports[0].nodePort}'" % namespace
    istio_ingress_nodeport_bytes = _subprocess.check_output(cmd, shell=True)
    return istio_ingress_nodeport_bytes.decode('utf-8')


def _get_istio_ingress_ip(namespace):
    cmd = "kubectl -n %s get po -l istio=ingress -o jsonpath='{.items[0].status.hostIP}'" % namespace
    istio_ingress_nodeport_bytes = _subprocess.check_output(cmd, shell=True)
    return istio_ingress_nodeport_bytes.decode('utf-8')


# TODO: Filter ingresses using image_registry_namespace ('predict-')
# Note:  This is used by multiple functions, so double-check before making changes here
def _get_all_model_endpoints(namespace,
                             image_registry_namespace=_default_image_registry_predict_namespace):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    endpoint_list = []
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        ingresses = kubeclient_v1_beta1.list_namespaced_ingress(namespace=namespace)
        for ingress in ingresses.items:
            endpoint = None
            if ingress.status.load_balancer.ingress and len(ingress.status.load_balancer.ingress) > 0:
                if (ingress.status.load_balancer.ingress[0].hostname):
                    endpoint = ingress.status.load_balancer.ingress[0].hostname
                if (ingress.status.load_balancer.ingress[0].ip):
                    endpoint = ingress.status.load_balancer.ingress[0].ip

            if not endpoint:
                try:
                    istio_ingress_nodeport = _get_istio_ingress_nodeport(namespace)
                except Exception:
                    istio_ingress_nodeport = '<ingress-controller-nodeport>'

                try:
                    istio_ingress_ip = _get_istio_ingress_ip(namespace)
                except Exception:
                    istio_ingress_ip = '<ingress-controller-ip>'

                endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

            path = ingress.spec.rules[0].http.paths[0].path
            endpoint = 'http://%s%s' % (endpoint, path)
            endpoint = endpoint.replace(".*", "invoke")
            endpoint_list += [endpoint]

    return endpoint_list


def _get_cluster_service(service_name,
                         namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()

    endpoint = None
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")
        service = kubeclient_v1.read_namespaced_service(name=service_name,
                                                        namespace=namespace)

        # TODO: What about port? defaults to 80 for ingress controller, but what about non-ingress-controller?
        if service.status.load_balancer.ingress and len(service.status.load_balancer.ingress) > 0:
            if (service.status.load_balancer.ingress[0].hostname):
                endpoint = service.status.load_balancer.ingress[0].hostname
            if (service.status.load_balancer.ingress[0].ip):
                endpoint = service.status.load_balancer.ingress[0].ip

        if not endpoint:
            try:
                istio_ingress_nodeport = _get_istio_ingress_nodeport(namespace)
            except Exception:
                istio_ingress_nodeport = '<ingress-controller-nodeport>'

            try:
                istio_ingress_ip = _get_istio_ingress_ip(namespace)
            except Exception:
                istio_ingress_ip = '<ingress-controller-ip>'

            endpoint = '%s:%s' % (istio_ingress_ip, istio_ingress_nodeport)

    return endpoint


def _istio_apply(yaml_path,
                 namespace=None):

    if not namespace:
        namespace = _default_namespace

    yaml_path = _os.path.normpath(yaml_path)

    cmd = "istioctl kube-inject -i %s -f %s" % (namespace, yaml_path)
    print("")
    print("Running '%s'." % cmd)
    print("")
    new_yaml_bytes = _subprocess.check_output(cmd, shell=True)
    new_yaml_path = '%s-istio' % yaml_path
    with open(new_yaml_path, 'wt') as fh:
        fh.write(new_yaml_bytes.decode('utf-8'))
        print("'%s' => '%s'" % (yaml_path, new_yaml_path))
    print("")

    cmd = "kubectl apply --namespace %s -f %s" % (namespace, new_yaml_path)
    print("")
    print("Running '%s'." % cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")


def predict_kube_route(
    model_name,
    model_split_tag_and_weight_dict,
    model_shadow_tag_list,
    pipeline_templates_path=None,
    image_registry_namespace=None,
    namespace=None
):
    """
    Route and shadow traffic across model variant services.

    Examples:
    {"cpu":50, "gpu":50} 
    {"cpu":1, "gpu":99} 
    {"025":99, "050":1}
    {"025":50, "050":50}
    {"025":1, "050":99}
    split: {"a":100, "b":0}
    shadow: ["b"]
    
    :param model_name:
    :param model_split_tag_and_weight_dict: Example: # '{"a":100, "b":0, "c":0}'
    :param model_shadow_tag_list: Example: '[b,c]' Note: must set b and c to traffic split 0 above
    :param pipeline_templates_path:
    :param image_registry_namespace:
    :param namespace:
    :return:
    """

    model_name = _validate_and_prep_model_name(model_name)

    if type(model_split_tag_and_weight_dict) is str:
        model_split_tag_and_weight_dict = _base64.b64decode(model_split_tag_and_weight_dict)
        model_split_tag_and_weight_dict = _json.loads(model_split_tag_and_weight_dict)

    if type(model_shadow_tag_list) is str:
        model_shadow_tag_list = _base64.b64decode(model_shadow_tag_list)
        # strip '[' and ']' and split on comma
        model_shadow_tag_list = model_shadow_tag_list.decode('utf-8')
        model_shadow_tag_list = model_shadow_tag_list.strip()
        model_shadow_tag_list = model_shadow_tag_list.lstrip('[')
        model_shadow_tag_list = model_shadow_tag_list.rstrip(']')
        if ',' in model_shadow_tag_list:
            model_shadow_tag_list = model_shadow_tag_list.split(',')
            model_shadow_tag_list = [tag.strip() for tag in model_shadow_tag_list]
            model_shadow_tag_list = [tag.strip("\"") for tag in model_shadow_tag_list]
        else:
            model_shadow_tag_list = model_shadow_tag_list.strip("\"")
            if model_shadow_tag_list:
                model_shadow_tag_list = [model_shadow_tag_list]
            else:
                model_shadow_tag_list = []

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    try:
        _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict)
    except ValueError as ve:
        return_dict = {
            "status": "incomplete",
            "error_message": ve
        }

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict

    for model_tag in model_shadow_tag_list:
        error_message = '''
        Model variants targeted for traffic-shadow must also bet set to
        0 percent traffic-split as follows: 
        --model-split-tag-and-weight-dict=\'{"%s":0,...}\'.\' % model_tag
        '''
        try:
            if int(model_split_tag_and_weight_dict[model_tag]) != 0:
                return_dict = {
                    "status": "incomplete",
                    "error_message": error_message
                }
                if _http_mode:
                    return _jsonify(return_dict)
                else:
                    return return_dict
        except KeyError:
            return_dict = {
                "status": "incomplete",
                "error_message": error_message
            }
            if _http_mode:
                return _jsonify(return_dict)
            else:
                return return_dict

    model_shadow_tag_list = [_validate_and_prep_model_tag(model_tag) for model_tag in model_shadow_tag_list]
    model_split_tag_list = [_validate_and_prep_model_tag(model_tag) for model_tag in model_split_tag_and_weight_dict.keys()]
    model_split_weight_list = list(model_split_tag_and_weight_dict.values())
    context = {
        'PIPELINE_NAMESPACE': namespace,
        'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
        'PIPELINE_MODEL_NAME': model_name,
        'PIPELINE_MODEL_SPLIT_TAG_LIST': model_split_tag_list,
        'PIPELINE_MODEL_SPLIT_WEIGHT_LIST': model_split_weight_list,
        'PIPELINE_MODEL_NUM_SPLIT_TAGS_AND_WEIGHTS': len(model_split_tag_list),
        'PIPELINE_MODEL_SHADOW_TAG_LIST': model_shadow_tag_list,
        'PIPELINE_MODEL_NUM_SHADOW_TAGS': len(model_shadow_tag_list)
    }

    model_router_routerules_yaml_templates_path = _os.path.normpath(_os.path.join(
        pipeline_templates_path,
        _kube_router_routerules_template_registry['predict-router'][0][0])
    )
    path, filename = _os.path.split(model_router_routerules_yaml_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)

    # Operating systems limit the length of file names
    # Code below is commented because the generated yaml file name gets too long and raises
    # OSError: [Errno 36] File name too long
    # split_tag_weight_filename_snippet = 'split'
    # for idx in range(len(model_split_tag_list)):
    #     split_tag_weight_filename_snippet = '%s-%s-%s' % (split_tag_weight_filename_snippet, model_split_tag_list[idx], model_split_weight_list[idx])
    # split_tag_weight_filename_snippet = split_tag_weight_filename_snippet.lstrip('-')
    # split_tag_weight_filename_snippet = split_tag_weight_filename_snippet.rstrip('-')
    # shadow_tag_filename_snippet = 'shadow'
    # for idx in range(len(model_shadow_tag_list)):
    #     shadow_tag_filename_snippet = '%s-%s' % (shadow_tag_filename_snippet, model_shadow_tag_list[idx])
    # shadow_tag_filename_snippet = shadow_tag_filename_snippet.lstrip('-')
    # shadow_tag_filename_snippet = shadow_tag_filename_snippet.rstrip('-')
    # rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s-router-routerules.yaml' % (image_registry_namespace, model_name, split_tag_weight_filename_snippet, shadow_tag_filename_snippet))

    # refactoring rendered_filename
    # removing shadow_tag_filename_snippet and split_tag_weight_filename_snippet
    # to resolve OSError: [Errno 36] File name too long
    # refactored naming convention is limited to model name to match the
    # identifier being used to group, compare and route model variants
    rendered_filename = _os.path.normpath(
        '.pipeline-generated-%s-%s-router-routerules.yaml'
        % (image_registry_namespace, model_name)
    )
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_filename))
    _kube_apply(rendered_filename, namespace)

    return_dict = {
        "status": "complete",
        "model_split_tag_and_weight_dict": model_split_tag_and_weight_dict,
        "model_shadow_tag_list": model_shadow_tag_list
    }

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


# ie. http://localhost:32000/predict-kube-stop/mnist/a

def predict_kube_stop(model_name,
                      model_tag,
                      namespace=None,
                      image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    _service_stop(service_name=service_name,
                  namespace=namespace)

    # TODO:  Also remove from ingress

    return_dict = {"status": "complete",
                   "model_name": model_name,
                   "model_tag": model_tag}

    if _http_mode:
        return _jsonify(return_dict)
    else:
        return return_dict


def _service_stop(service_name,
                  namespace=None):

    if not namespace:
        namespace = _default_namespace

    _kubeconfig.load_kube_config()
    kubeclient_v1 = _kubeclient.CoreV1Api()
    kubeclient_v1_beta1 = _kubeclient.ExtensionsV1beta1Api()

    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore")

        # Remove deployment
        response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False, pretty=True)
        found = False
        deployments = response.items
        for deploy in deployments:
            if service_name in deploy.metadata.name:
                found = True
                break
        if found:
            print("")
            print("Deleting '%s' deployment." % deploy.metadata.name)
            print("")
            cmd = "kubectl delete deploy %s --namespace %s" % (deploy.metadata.name, namespace)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")

        # Remove service
        response = kubeclient_v1.list_service_for_all_namespaces(watch=False, pretty=True)
        found = False
        deployments = response.items
        for deploy in deployments:
            if service_name in deploy.metadata.name:
                found = True
                break
        if found:
            print("Deleting '%s' service." % deploy.metadata.name)
            print("")
            cmd = "kubectl delete svc %s --namespace %s" % (deploy.metadata.name, namespace)
            print("Running '%s'." % cmd)
            print("")
            _subprocess.call(cmd, shell=True)
            print("")


def train_server_pull(model_name,
                      model_tag,
                      image_registry_url=None,
                      image_registry_repo=None,
                      image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    cmd = 'docker pull %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def train_server_register(model_name,
                          model_tag,
                          image_registry_url=None,
                          image_registry_repo=None,
                          image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    cmd = 'docker push %s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def train_server_logs(model_name,
                      model_tag,
                      image_registry_namespace=None,
                      logs_cmd='docker'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    print("")
    cmd = '%s logs -f %s' % (logs_cmd, container_name)
    print(cmd)
    print("")

    _subprocess.call(cmd, shell=True)


def train_server_shell(model_name,
                       model_tag,
                       image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    cmd = 'docker exec -it %s bash' % container_name
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def _create_train_server_Dockerfile(model_name,
                                    model_tag,
                                    model_path,
                                    model_type,
                                    model_runtime,
                                    model_chip,
                                    stream_logger_url,
                                    stream_logger_topic,
                                    stream_input_url,
                                    stream_input_topic,
                                    stream_output_url,
                                    stream_output_topic,
                                    build_context_path,
                                    image_registry_url,
                                    image_registry_repo,
                                    image_registry_namespace,
                                    image_registry_base_tag,
                                    image_registry_base_chip,
                                    pipeline_templates_path):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    print("")
    print("Using templates in '%s'." % pipeline_templates_path)
    print("(Specify --pipeline-templates-path if the templates live elsewhere.)")
    print("")

    context = {
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_PATH': model_path,
               'PIPELINE_MODEL_TYPE': model_type,
               'PIPELINE_MODEL_RUNTIME': model_runtime,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
              }

    model_train_cpu_Dockerfile_templates_path = _os.path.normpath(_os.path.join(pipeline_templates_path, _Dockerfile_template_registry['train-server'][0][0]))
    path, filename = _os.path.split(model_train_cpu_Dockerfile_templates_path)
    rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
    rendered_filename = _os.path.normpath('%s/.pipeline-generated-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_name, model_tag))
    with open(rendered_filename, 'wt') as fh:
        fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_filename))

    return rendered_filename


#
# model_name: mnist
# model_tag: gpu
# model_path: tensorflow/mnist-gpu/model/
# model_type: tensorflow
# model_runtime: tfserving
# model_chip: gpu
#
def train_server_build(model_name,
                       model_tag,
                       model_path,
                       model_type,
                       model_runtime=None,
                       model_chip=None,
                       http_proxy=None,
                       https_proxy=None,
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       build_type=None,
                       build_context_path=None,
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       image_registry_base_chip=None,
                       pipeline_templates_path=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_runtime:
        model_runtime = _get_default_model_runtime(model_type)

    if not model_chip:
        model_chip = _default_model_chip

    if not build_type:
        build_type = _default_build_type

    if not build_context_path:
        build_context_path = _default_build_context_path

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    build_context_path = _os.path.normpath(build_context_path)
    build_context_path = _os.path.expandvars(build_context_path)
    build_context_path = _os.path.expanduser(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)
    build_context_path = _os.path.abspath(build_context_path)
    build_context_path = _os.path.normpath(build_context_path)
    print(build_context_path)

    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    pipeline_templates_path = _os.path.relpath(pipeline_templates_path, build_context_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)
    print(pipeline_templates_path)

    model_path = _os.path.normpath(model_path)
    model_path = _os.path.expandvars(model_path)
    model_path = _os.path.expanduser(model_path)
    model_path = _os.path.abspath(model_path)
    model_path = _os.path.normpath(model_path)
    model_path = _os.path.relpath(model_path, build_context_path)
    model_path = _os.path.normpath(model_path)
    print(model_path)

    if build_type == 'docker':
        generated_Dockerfile = _create_train_server_Dockerfile(model_name=model_name,
                                                               model_tag=model_tag,
                                                               model_path=model_path,
                                                               model_type=model_type,
                                                               model_runtime=model_runtime,
                                                               model_chip=model_chip,
                                                               stream_logger_url=stream_logger_url,
                                                               stream_logger_topic=stream_logger_topic,
                                                               stream_input_url=stream_input_url,
                                                               stream_input_topic=stream_input_topic,
                                                               stream_output_url=stream_output_url,
                                                               stream_output_topic=stream_output_topic,
                                                               build_context_path=build_context_path,
                                                               image_registry_url=image_registry_url,
                                                               image_registry_repo=image_registry_repo,
                                                               image_registry_namespace=image_registry_namespace,
                                                               image_registry_base_tag=image_registry_base_tag,
                                                               image_registry_base_chip=image_registry_base_chip,
                                                               pipeline_templates_path=pipeline_templates_path)

        if http_proxy:
            http_proxy_build_arg_snippet = '--build-arg HTTP_PROXY=%s' % http_proxy
        else:
            http_proxy_build_arg_snippet = ''

        if https_proxy:
            https_proxy_build_arg_snippet = '--build-arg HTTPS_PROXY=%s' % https_proxy
        else:
            https_proxy_build_arg_snippet = ''

        cmd = 'docker build %s %s -t %s/%s/%s-%s:%s -f %s %s' % (http_proxy_build_arg_snippet, https_proxy_build_arg_snippet, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag, generated_Dockerfile, build_context_path)

        print(cmd)
        print("")
        _subprocess.call(cmd, shell=True)
    else:
        print("Build type '%s' not found." % build_type)


def train_server_start(model_name,
                       model_tag,
                       input_host_path,
                       output_host_path,
                       training_runs_host_path,
                       train_args,
                       single_server_only='true',
                       stream_logger_url=None,
                       stream_logger_topic=None,
                       stream_input_url=None,
                       stream_input_topic=None,
                       stream_output_url=None,
                       stream_output_topic=None,
                       memory_limit=None,
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       start_cmd='docker',
                       start_cmd_extra_args=''):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if _is_base64_encoded(input_host_path):
        input_host_path = _decode_base64(input_host_path)
    input_host_path = _os.path.expandvars(input_host_path)
    input_host_path = _os.path.expanduser(input_host_path)
    input_host_path = _os.path.normpath(input_host_path)
    input_host_path = _os.path.abspath(input_host_path)

    if _is_base64_encoded(output_host_path):
        output_host_path = _decode_base64(output_host_path)
    output_host_path = _os.path.expandvars(output_host_path)
    output_host_path = _os.path.expanduser(output_host_path)
    output_host_path = _os.path.normpath(output_host_path)
    output_host_path = _os.path.abspath(output_host_path)

    if _is_base64_encoded(training_runs_host_path):
        training_runs_host_path = _decode_base64(training_runs_host_path)
    training_runs_host_path = _os.path.expandvars(training_runs_host_path)
    training_runs_host_path = _os.path.expanduser(training_runs_host_path)
    training_runs_host_path = _os.path.normpath(training_runs_host_path)
    training_runs_host_path = _os.path.abspath(training_runs_host_path)

    if _is_base64_encoded(train_args):
        train_args = _decode_base64(train_args)
    # Note:  train_args are not currently expanded, so they are handled as is
    #        in other words, don't expect ~ to become /Users/cfregly/..., etc like the above paths
    #        the logic below isn't working properly.  it creates the following in the Docker cmd:
    #        -e PIPELINE_TRAIN_ARGS="/Users/cfregly/pipelineai/models/tensorflow/mnist-v3/model/--train_epochs=2 --batch_size=100
    # train_args = _os.path.expandvars(train_args)
    # train_args = _os.path.expanduser(train_args)
    # train_args = _os.path.normpath(train_args)
    # train_args = _os.path.abspath(train_args)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    # Trying to avoid this:
    #   WARNING: Your kernel does not support swap limit capabilities or the cgroup is not mounted. Memory limited without swap.
    #
    # https://docs.docker.com/config/containers/resource_constraints/#limit-a-containers-access-to-memory
    #
    if not memory_limit:
        memory_limit = ''
    else:
        memory_limit = '--memory=%s --memory-swap=%s' % (memory_limit, memory_limit)

    # environment == local, task type == worker, and no cluster definition
    tf_config_local_run = '\'{\"environment\": \"local\", \"task\":{\"type\": \"worker\"}}\''

    # Note:  We added `train` to mimic AWS SageMaker and encourage ENTRYPOINT vs CMD per https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html
    # /opt/ml/input/data/{training|validation|testing} per https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo.html

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    # Note:  The %s:<paths> below must match the paths in templates/docker/train-server-local-dockerfile.template
    # Any changes to these paths must be sync'd with train-server-local-dockerfile.template, train-cluster.yaml.template, and train-cluster-gpu.yaml.template
    # Also, /opt/ml/model is already burned into the Docker image at this point, so we can't specify it from the outside.  (This is by design.)
    cmd = '%s run -itd -p 2222:2222 -p 6006:6006 -e PIPELINE_SINGLE_SERVER_ONLY=%s -e PIPELINE_STREAM_LOGGER_URL=%s -e PIPELINE_STREAM_LOGGER_TOPIC=%s -e PIPELINE_STREAM_INPUT_URL=%s -e PIPELINE_STREAM_INPUT_TOPIC=%s -e PIPELINE_STREAM_OUTPUT_URL=%s -e PIPELINE_STREAM_OUTPUT_TOPIC=%s -e TF_CONFIG=%s -e PIPELINE_TRAIN_ARGS="%s" -v %s:/opt/ml/input/ -v %s:/opt/ml/output/ -v %s:/root/pipelineai/training_runs/ --name=%s %s %s %s/%s/%s-%s:%s train' % (start_cmd, single_server_only, stream_logger_url, stream_logger_topic, stream_input_url, stream_input_topic, stream_output_url, stream_output_topic, tf_config_local_run, train_args, input_host_path, output_host_path, training_runs_host_path, container_name, memory_limit, start_cmd_extra_args, image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag)
    print("")
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)
    print("")
    print("==> IGNORE ANY 'WARNING' ABOVE.  IT'S WORKING OK!!")
    print("")
    print("Container start: %s" % container_name)
    print("")
    print("==> Use 'pipeline train-server-logs --model-name=%s --model-tag=%s' to see the container logs." % (model_name, model_tag))
    print("")


def train_server_stop(model_name,
                      model_tag,
                      image_registry_namespace=None,
                      stop_cmd='docker'):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    container_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)
    print("")
    cmd = '%s rm -f %s' % (stop_cmd, container_name)
    print(cmd)
    print("")
    _subprocess.call(cmd, shell=True)


def _create_train_kube_yaml(model_name,
                            model_tag,
                            input_host_path,
                            output_host_path,
                            training_runs_host_path,
                            model_chip,
                            train_args,
                            stream_logger_url,
                            stream_logger_topic,
                            stream_input_url,
                            stream_input_topic,
                            stream_output_url,
                            stream_output_topic,
                            master_replicas,
                            ps_replicas,
                            worker_replicas,
                            image_registry_url,
                            image_registry_repo,
                            image_registry_namespace,
                            image_registry_base_tag,
                            image_registry_base_chip,
                            pipeline_templates_path,
                            namespace):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    context = {
               'PIPELINE_NAMESPACE': namespace,
               'PIPELINE_MODEL_NAME': model_name,
               'PIPELINE_MODEL_TAG': model_tag,
               'PIPELINE_MODEL_CHIP': model_chip,
               'PIPELINE_TRAIN_ARGS': train_args,
               'PIPELINE_INPUT_HOST_PATH': input_host_path,
               'PIPELINE_OUTPUT_HOST_PATH': output_host_path,
               'PIPELINE_TRAINING_RUNS_HOST_PATH': training_runs_host_path,
               'PIPELINE_STREAM_LOGGER_URL': stream_logger_url,
               'PIPELINE_STREAM_LOGGER_TOPIC': stream_logger_topic,
               'PIPELINE_STREAM_INPUT_URL': stream_input_url,
               'PIPELINE_STREAM_INPUT_TOPIC': stream_input_topic,
               'PIPELINE_STREAM_OUTPUT_URL': stream_output_url,
               'PIPELINE_STREAM_OUTPUT_TOPIC': stream_output_topic,
               'PIPELINE_MASTER_REPLICAS': int(master_replicas),
               'PIPELINE_PS_REPLICAS': int(ps_replicas),
               'PIPELINE_WORKER_REPLICAS': int(worker_replicas),
               'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
               'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
               'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
               'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag,
               'PIPELINE_IMAGE_REGISTRY_BASE_CHIP': image_registry_base_chip,
               }

    if model_chip == 'gpu':
        predict_clustered_template = _os.path.normpath(_os.path.join(pipeline_templates_path, _train_kube_template_registry['train-gpu-cluster'][0][0]))
        path, filename = _os.path.split(predict_clustered_template)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
    else:
        predict_clustered_template = _os.path.normpath(_os.path.join(pipeline_templates_path, _train_kube_template_registry['train-cluster'][0][0]))
        path, filename = _os.path.split(predict_clustered_template)
        rendered = _jinja2.Environment(loader=_jinja2.FileSystemLoader(path)).get_template(filename).render(context)
        rendered_filename = _os.path.normpath('.pipeline-generated-%s-%s-%s-%s.yaml' % (image_registry_namespace, model_name, model_tag, model_chip))
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)

    print("'%s' => '%s'." % (filename, rendered_filename))

    return rendered_filename


def train_kube_connect(model_name,
                       model_tag,
                       local_port=None,
                       service_port=None,
                       namespace=None,
                       image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_connect(service_name=service_name,
                     namespace=namespace,
                     local_port=local_port,
                     service_port=service_port)


def train_kube_describe(model_name,
                        model_tag,
                        namespace=None,
                        image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    return _service_describe(service_name=service_name,
                             namespace=namespace)


def train_kube_shell(model_name,
                     model_tag,
                     namespace=None,
                     image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_shell(service_name=service_name,
                   namespace=namespace)


def train_kube_start(model_name,
                     model_tag,
                     input_host_path,
                     output_host_path,
                     training_runs_host_path,
                     train_args,
                     model_chip=None,
                     master_replicas=1,
                     ps_replicas=1,
                     worker_replicas=1,
                     stream_logger_url=None,
                     stream_logger_topic=None,
                     stream_input_url=None,
                     stream_input_topic=None,
                     stream_output_url=None,
                     stream_output_topic=None,
                     image_registry_url=None,
                     image_registry_repo=None,
                     image_registry_namespace=None,
                     image_registry_base_tag=None,
                     image_registry_base_chip=None,
                     pipeline_templates_path=None,
                     namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not model_chip:
        model_chip = _default_model_chip

    print(input_host_path)

    if _is_base64_encoded(input_host_path):
        input_host_path = _decode_base64(input_host_path)
    input_host_path = _os.path.expandvars(input_host_path)
    input_host_path = _os.path.expanduser(input_host_path)
    input_host_path = _os.path.normpath(input_host_path)
    input_host_path = _os.path.abspath(input_host_path)

    if _is_base64_encoded(output_host_path):
        output_host_path = _decode_base64(output_host_path)
    output_host_path = _os.path.expandvars(output_host_path)
    output_host_path = _os.path.expanduser(output_host_path)
    output_host_path = _os.path.normpath(output_host_path)
    output_host_path = _os.path.abspath(output_host_path)

    if _is_base64_encoded(training_runs_host_path):
        training_runs_host_path = _decode_base64(training_runs_host_path)
    training_runs_host_path = _os.path.expandvars(training_runs_host_path)
    training_runs_host_path = _os.path.expanduser(training_runs_host_path)
    training_runs_host_path = _os.path.normpath(training_runs_host_path)
    training_runs_host_path = _os.path.abspath(training_runs_host_path)

    if _is_base64_encoded(train_args):
        train_args = _decode_base64(train_args)
    train_args = _os.path.expandvars(train_args)
    train_args = _os.path.expanduser(train_args)
    train_args = _os.path.normpath(train_args)
    train_args = _os.path.abspath(train_args)

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not image_registry_base_chip:
        image_registry_base_chip = model_chip

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    pipeline_templates_path = _os.path.expandvars(pipeline_templates_path)
    pipeline_templates_path = _os.path.expanduser(pipeline_templates_path)
    pipeline_templates_path = _os.path.abspath(pipeline_templates_path)
    pipeline_templates_path = _os.path.normpath(pipeline_templates_path)

    if not namespace:
        namespace = _default_namespace

    generated_yaml_path = _create_train_kube_yaml(model_name=model_name,
                                                  model_tag=model_tag,
                                                  model_chip=model_chip,
                                                  input_host_path=input_host_path,
                                                  output_host_path=output_host_path,
                                                  training_runs_host_path=training_runs_host_path,
                                                  train_args=train_args,
                                                  stream_logger_url=stream_logger_url,
                                                  stream_logger_topic=stream_logger_topic,
                                                  stream_input_url=stream_input_url,
                                                  stream_input_topic=stream_input_topic,
                                                  stream_output_url=stream_output_url,
                                                  stream_output_topic=stream_output_topic,
                                                  master_replicas=master_replicas,
                                                  ps_replicas=ps_replicas,
                                                  worker_replicas=worker_replicas,
                                                  image_registry_url=image_registry_url,
                                                  image_registry_repo=image_registry_repo,
                                                  image_registry_namespace=image_registry_namespace,
                                                  image_registry_base_tag=image_registry_base_tag,
                                                  image_registry_base_chip=image_registry_base_chip,
                                                  pipeline_templates_path=pipeline_templates_path,
                                                  namespace=namespace)

    generated_yaml_path = _os.path.normpath(generated_yaml_path)

    # For now, only handle '-deploy' and '-svc' yaml's
    _kube_apply(yaml_path=generated_yaml_path,
                namespace=namespace)


def train_kube_stop(model_name,
                    model_tag,
                    namespace=None,
                    image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_stop(service_name=service_name,
                         namespace=namespace)


def train_kube_logs(model_name,
                    model_tag,
                    namespace=None,
                    image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_logs(service_name=service_name,
                         namespace=namespace)


def train_kube_scale(model_name,
                     model_tag,
                     replicas,
                     namespace=None,
                     image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_train_namespace

    service_name = '%s-%s-%s' % (image_registry_namespace, model_name, model_tag)

    _service_scale(service_name=service_name,
                   replicas=replicas,
                   namespace=namespace)


def predict_sage_start(model_name,
                       model_tag,
                       aws_iam_arn,
                       namespace=None,
                       image_registry_url=None,
                       image_registry_repo=None,
                       image_registry_namespace=None,
                       image_registry_base_tag=None,
                       pipeline_templates_path=None):

    model_name = _validate_and_prep_model_name(model_name)
    model_tag = _validate_and_prep_model_tag(model_tag)

    if not namespace:
        namespace = _default_namespace

    if not image_registry_url:
        image_registry_url = _default_image_registry_url

    if not image_registry_repo:
        image_registry_repo = _default_image_registry_repo

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    if not image_registry_base_tag:
        image_registry_base_tag = _default_image_registry_base_tag

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    # Create Model
    begin_time = _datetime.now()

    sagemaker_admin_client = _boto3.client('sagemaker')
    response = sagemaker_admin_client.create_model(
        ModelName='%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
        PrimaryContainer={
            'ContainerHostname': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'Image': '%s/%s/%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_name, model_tag),
            'Environment': {
            }
        },
        ExecutionRoleArn='%s' % aws_iam_arn,
        Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
#            {
#                'Key': 'PIPELINE_MODEL_TYPE',
#                'Value': '%s' % model_type
#            },
#            {
#                'Key': 'PIPELINE_MODEL_RUNTIME',
#                'Value': '%s' % model_runtime
#            },
#            {
#                'Key': 'PIPELINE_MODEL_CHIP',
#                'Value': '%s' % model_chip
#            },
        ]
    )

    model_region = 'UNKNOWN_REGION'
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        model_arn = response['ModelArn']
        print("")
        print("ModelArn: '%s'" % model_arn)
        model_region = model_arn.split(':')[3]
        print("")
    else:
        return

    end_time = _datetime.now()

    total_time = end_time - begin_time
    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return _get_sage_endpoint_url(model_name=model_name,
                                  model_region=model_region,
                                  image_registry_namespace=image_registry_namespace)


# TODO:  Verify that this works now that AWS SageMaker has fixed a bug
#
#   aws sagemaker update-endpoint-weights-and-capacities --endpoint-name=arn:aws:sagemaker:us-west-2:954636985443:endpoint-config/predict-mnist --desired-weights-and-capacities='[{"VariantName": "predict-mnist-gpu", "DesiredWeight": 100, "DesiredInstanceCount": 1}]'
#
#   aws sagemaker update-endpoint-weights-and-capacities --endpoint-name=arn:aws:sagemaker:us-west-2:954636985443:endpoint-config/predict-mnist --desired-weights-and-capacities=VariantName=predict-mnist-gpu,DesiredWeight=100,DesiredInstanceCount=1
#
def predict_sage_route(model_name,
                       aws_instance_type_dict,
                       model_split_tag_and_weight_dict,
                       pipeline_templates_path=None,
                       image_registry_namespace=None):

    model_name = _validate_and_prep_model_name(model_name)

    # Instance Types:
    #   'ml.c4.2xlarge'|'ml.c4.8xlarge'|'ml.c4.xlarge'|'ml.c5.2xlarge'|'ml.c5.9xlarge'|'ml.c5.xlarge'|'ml.m4.xlarge'|'ml.p2.xlarge'|'ml.p3.2xlarge'|'ml.t2.medium',
    if type(aws_instance_type_dict) is str:
        aws_instance_type_dict = _base64.b64decode(aws_instance_type_dict)
        aws_instance_type_dict = _json.loads(aws_instance_type_dict)

    if type(model_split_tag_and_weight_dict) is str:
        model_split_tag_and_weight_dict = _base64.b64decode(model_split_tag_and_weight_dict)
        model_split_tag_and_weight_dict = _json.loads(model_split_tag_and_weight_dict)

    if not pipeline_templates_path:
        pipeline_templates_path = _default_pipeline_templates_path

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    try:
        _validate_and_prep_model_split_tag_and_weight_dict(model_split_tag_and_weight_dict)
    except ValueError as ve:
        return_dict = {"status": "incomplete",
                       "error_message": ve}

        if _http_mode:
            return _jsonify(return_dict)
        else:
            return return_dict

    model_tag_list = [ _validate_and_prep_model_tag(model_tag) for model_tag in model_split_tag_and_weight_dict.keys() ]

    sagemaker_admin_client = _boto3.client('sagemaker')

    begin_time = _datetime.now()

    if not _get_sage_endpoint_config(model_name):
        # Create Endpoint Configuration
        tag_weight_dict_list = []

        for model_tag in model_tag_list:
            tag_weight_dict = {
            'VariantName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'ModelName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'InitialInstanceCount': 1,
            'InstanceType': '%s' % aws_instance_type_dict[model_tag],
            'InitialVariantWeight': model_split_tag_and_weight_dict[model_tag],
            }

            tag_weight_dict_list += [tag_weight_dict]

        print(tag_weight_dict_list)

        response = sagemaker_admin_client.create_endpoint_config(
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
            ProductionVariants=tag_weight_dict_list,
            Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
            ]
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointConfigArn: '%s'" % response['EndpointConfigArn'])
            print("")
        else:
            return
    else:
        tag_weight_dict_list = []

        for model_tag in model_tag_list:
            tag_weight_dict = {
            'VariantName': '%s-%s-%s' % (image_registry_namespace, model_name, model_tag),
            'DesiredWeight': model_split_tag_and_weight_dict[model_tag],
            'DesiredInstanceCount': 1
            }

            tag_weight_dict_list += [tag_weight_dict]

        print(tag_weight_dict_list)

        response = sagemaker_admin_client.update_endpoint_weights_and_capacities(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
            DesiredWeightsAndCapacities=tag_weight_dict_list,
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointArn: '%s'" % response['EndpointArn'])
            print("")
        else:
            print(response['ResponseMetadata']['HTTPStatusCode'])
            return

    if not _get_sage_endpoint(model_name):
        # Create Endpoint (Models + Endpoint Configuration)
        response = sagemaker_admin_client.create_endpoint(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
            Tags=[
            {
                'Key': 'PIPELINE_MODEL_NAME',
                'Value': '%s' % model_name
            },
            {
                'Key': 'PIPELINE_MODEL_TAG',
                'Value': '%s' % model_tag
            },
            ]
        )

        if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("")
            print("EndpointArn: '%s'" % response['EndpointArn'])
            print("")
        else:
            return

    end_time = _datetime.now()

    total_time = end_time - begin_time

    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")


def _get_sage_endpoint_config(model_name,
                              image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    sagemaker_admin_client = _boto3.client('sagemaker')

    begin_time = _datetime.now()

    try:
        response = sagemaker_admin_client.describe_endpoint_config(
            EndpointConfigName='%s-%s' % (image_registry_namespace, model_name),
        )
    except _ClientError:
        return None

    end_time = _datetime.now()

    total_time = end_time - begin_time

    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        print("EndpointConfigArn: '%s'" % response['EndpointConfigArn'])
        print("")
    else:
        print(response['ResponseMetadata']['HTTPStatusCode'])
        return

    print("")
    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return response['EndpointConfigArn']


def _get_sage_endpoint(model_name,
                       image_registry_namespace=None):

    if not image_registry_namespace:
        image_registry_namespace = _default_image_registry_predict_namespace

    sagemaker_admin_client = _boto3.client('sagemaker')

    begin_time = _datetime.now()

    try:
        response = sagemaker_admin_client.describe_endpoint(
            EndpointName='%s-%s' % (image_registry_namespace, model_name),
        )
    except _ClientError:
        return None

    end_time = _datetime.now()

    total_time = end_time - begin_time

    model_region = 'UNKNOWN_REGION'
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("")
        model_arn = response['EndpointArn']
        print("EndpointArn: '%s'" % model_arn)
        model_region = model_arn.split(':')[3]
    else:
        print(response['ResponseMetadata']['HTTPStatusCode'])
        return

    print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
    print("")

    return _get_sage_endpoint_url(model_name,
                                  model_region,
                                  image_registry_namespace)


def _main():
    #  WARNING:
    #      the global variables below DO NOT WORK
    #      the values are only available within this main(), not the code above
    global _http_mode

    print(_sys.argv)

    if len(_sys.argv) == 1:
        return help()
    else:
        _http_mode = False
        _fire.Fire()


if __name__ == '__main__':
    _main()
