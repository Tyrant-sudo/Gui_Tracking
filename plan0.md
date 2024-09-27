1. review the route
   1. Using `choose_position.ipynb` to choose the first position.
   2. Using `Single Object Tracking.ipynb` to get all position and tracking them.
   3. Using `csv_process.ipynb` to fitting and output.
2. get the methods to set GUI
3. rewrite the code
4. prepare the example

# Files Prepared

1. Required pytorch libraries:
   1. For NNs: pytorch...
   2. For tracking: mmtracking...
   3. For GUIL: pyQt...
2. Code for tracking, code for extracting
3. Neural Networks
   1. For tracking: siamese_rpn
   2. For finding lines: twist_test
4. Pictures
5. Examples

# GUI

1. 框选多个起始点
   1. 最上方输入图片路径
   2. 中间出现图片
   3. 框选图片位置
   4. 自动分组读取框的坐标
      1. 选取时图片上方显示“第N组”，N为当前选取的组数
      2. “第N组”右侧显示“下一组”，“取消”字样
      3. 按图片下方确定键确认，取消键取消
      4. 选取到足够的数目点击下一组，此时
   5. 在按钮下方显示框的左上角、右下角值
      1. 可以删除
      2. 每选取一个值，列表增加
      3. 需要显示值属于哪一组
      4. 超过6个会超出显示范围，需要上下拉动


# GUI 1

1. 点选起点（0帧）
2. 点选终点（输入帧）
3. 输出twist
