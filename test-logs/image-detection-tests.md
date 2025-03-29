# YoloV5 On Device Tests

A log of tests done with different YoloV5n models.

## ONNX Model Tests

- `Input Size` : Input size of the image used by the model.
- `Average Inference Time`: The average time taken to do an inference task on the Raspberry Pi Zero 2W over 60 iterations.
- `Average FPS`: The average refresh rate on the Raspberry Pi Zero 2W when running this model in main.py.

    - Note: the maximum frame rate is 6fps.

- `Image Detection Quality`: How well the model can detect images in real time using the Raspberry Pi Camera Module 2.

| Input Size | Average Inference Time (Quadcore) | Average Inference Time (3 Core) | Average fps  | Image Detection Quality                          |
| ---------- | --------------------------------- | ------------------------------- | ------------ | ------------------------------------------------ |
| 128        | 0.08s                             | Not Done                        | Not Done     | Not consistent.                                  |
| 160        | 0.12s                             | Not Done                        | Not Done     | Better, but only if objects are close.           |
| 192        | 0.17s                             | 0.18s                           | 5-6fps       | Can detect from further, but avg. fps is 5-6fps. |
| 224        | 0.23s                             | 0.23s                           | 4fps         | Consistent, but distance is still a problem.     |
| 256        | 0.28s                             | 0.30s                           | 3fps         | Best, but distance is still not very good.       |


## CPU Core Usage

- 192x192

![ONNX Quadcore Image](imgs\onnx-quadcore-192.png)

- 224x224

![ONNX Quadcore Image](imgs\onnx-quadcore-224.png)

- 256x256

![ONNX Quadcore Image](imgs\onnx-quadcore-256.png)