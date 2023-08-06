from aquests import configure


freeze_graph --input_checkpoint=resources/chkpoint/acc-0.8710000+cost-0.9503008-4851 \
    --input_graph=resources/exported/lge7/70/graph-def.pb \
    --input_binary=true \
    --output_node_names=concat \
    --output_graph=resources/exported/lge7/70/frozen-graph.pb

toco --graph_def_file=resources/exported/lge7/100/frozen-graph-def.pb \
  --output_format=TFLITE \
  --output_file=resources/exported/lge7/100/model.tflite \
  --input_arrays=Placeholder \
  --output_arrays=concat \
  --inference_type=QUANTIZED_UINT8 \
  --inference_input_type=QUANTIZED_UINT8 \
  --std_dev_values=128 \
  --mean_values=128 \
  --default_ranges_min=-1 \
  --default_ranges_max=6

toco --graph_def_file=resources/exported/lge7/70/frozen-graph.pb \
  --output_format=TFLITE \
  --output_file=resources/exported/lge7/70/model.tflite \
  --input_arrays=Placeholder \
  --output_arrays=concat  

---------------------------------------------------

TF 1.8

sudo apt-get install openjdk-8-jdk
echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
curl https://bazel.build/bazel-release.pub.gpg | sudo apt-key add -
sudo apt-get update && sudo apt-get install bazel
sudo apt-get upgrade bazel
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
git checkout r1.8
sudo apt-get install python-numpy python-dev python-pip python-wheel
./configure
bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package
bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package

bazel build tensorflow/contrib/lite/toco:toco
bazel-bin/tensorflow/contrib/lite/toco/toco


cd ~/sns/tensorflow

bazel-bin/tensorflow/contrib/lite/toco/toco --input_file=../aimdv/engine2/resources/exported/lge7/100/frozen-graph-def.pb \
  --input_format=TENSORFLOW_GRAPHDEF \
  --output_format=TFLITE \
  --output_file=../aimdv/engine2/resources/exported/lge7/100/model.tflite \
  --input_arrays=Placeholder \
  --output_arrays=concat \
  --inference_type=QUANTIZED_UINT8 \
  --inference_input_type=QUANTIZED_UINT8 \
  --std_dev_values=128 \
  --mean_values=128 \
  --default_ranges_min=-1 \
  --default_ranges_max=6 \
  --input_shapes=1,12,499
  
  bazel-bin/tensorflow/contrib/lite/toco/toco --input_file=../aimdv/engine2/resources/exported/lge7/100/frozen-graph-def.pb \
  --input_format=TENSORFLOW_GRAPHDEF \
  --output_format=TFLITE \
  --output_file=../aimdv/engine2/resources/exported/lge7/100/model.tflite \
  --input_arrays=Placeholder \
  --output_arrays=concat \
  --input_shapes=1,12,499
  