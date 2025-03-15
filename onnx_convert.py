import onnx
from onnxconverter_common import float16
from onnxruntime.quantization import quantize_dynamic, QuantType

def convert_to_fp16():
    # Load FP32 ONNX model
    model_fp32 = onnx.load("model/yolov5n.onnx")

    # Convert model to FP16
    model_fp16 = float16.convert_float_to_float16(model_fp32)

    # Save FP16 ONNX model
    onnx.save(model_fp16, "model/yolov5n_fp16.onnx")
    print("✅ FP16 model saved as yolov5n_fp16.onnx")

def convert_to_int8():

    # Load and quantize the ONNX model
    quantize_dynamic("model/yolov5n.onnx", "model/yolov5n_int8.onnx", weight_type=QuantType.QInt8)

    print("✅ INT8 model saved as yolov5n_int8.onnx")

if __name__ == "__main__":
    convert_to_int8()

    model = onnx.load("model/yolov5n_int8.onnx")

    for input_tensor in model.graph.input:
        print(f"Input: {input_tensor.name}, Type: {input_tensor.type.tensor_type.elem_type}")

    for output_tensor in model.graph.output:
        print(f"Output: {output_tensor.name}, Type: {output_tensor.type.tensor_type.elem_type}")
