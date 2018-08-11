import cv2
import sys
import numpy as np

#obtained through experiment 
pattern1_thresh = 220
pattern2_thresh = 210
min_connected_len = 20

def whichPattern(image):
	hist = cv2.calcHist([image], [0], None, [256], [0, 256])
	# pattern1 images has almost more than 600 pixels
	# for 0(pure black) intensity, lets set threshold to 500
	thresh = 500	
	if(hist[0, 0] > thresh):
		return 1
	else:
		return 2

# Separates the image <file> to six subimages containing each digit
# With an attempt to internally eliminate noise and color inversion
def separate_image(file):
	srcImage = cv2.imread(file, 0)

	pattern = whichPattern(srcImage) # determine the pattern of the image

	thresh = pattern1_thresh if pattern == 1 else pattern2_thresh

	ret, threshImage = cv2.threshold(srcImage, thresh, 255, cv2.THRESH_BINARY_INV)
	
	numLabel, labelImage, stats, centroids = cv2.connectedComponentsWithStats(threshImage, 8, cv2.CV_32S)
	
	# holds if compenet will be included to foreground
	foreComps = [i for i in range(1, numLabel) if stats[i, cv2.CC_STAT_AREA] >= min_connected_len]
	
	
	minCol = 30; # seen that all digits start at 30th column 
				 # no need for additional computation
	
	binaryImage = np.zeros_like(srcImage)
	labelImage = np.array(labelImage)
	for k in [np.where(labelImage == i) for i in foreComps]:
		binaryImage[k] = 255
	

	array = np.array([stats[i, cv2.CC_STAT_LEFT] + stats[i, cv2.CC_STAT_WIDTH]  for i in foreComps])
	maxCol = max(array[np.where(array < 125)])
		
	if pattern == 2:
		if maxCol <= 111:
			maxCol = 111
		elif maxCol < 117:
			maxCol = 117

	minRow = min([stats[i, cv2.CC_STAT_TOP] for i in foreComps])
	maxRow = max([stats[i, cv2.CC_STAT_TOP] + stats[i, cv2.CC_STAT_HEIGHT] for i in foreComps])

	subImage = binaryImage[minRow:maxRow, minCol:maxCol]
	subImage1 = subImage[:, :int(subImage.shape[1]/2)]
	subImage2 = subImage[:, int(subImage.shape[1]/2):]

	colIncrement1 = subImage1.shape[1] / 3
	colIncrement2 = subImage2.shape[1] / 3
	
	digitList1 = []
	digitList2 = []
	
	col1 = 0
	col2 = 0
	for i in range(2):
		digitList1.append(subImage1[:, int(col1):int(col1+colIncrement1)])
		digitList2.append(subImage2[:, int(col2):int(col2+colIncrement2)])
		col1 += colIncrement1
		col2 += colIncrement2

	digitList1.append(subImage1[:, int(col1):])
	digitList2.append(subImage2[:, int(col2):])

	return digitList1 + digitList2
  
def divDigits(args):
	if(len(args) != 5):
		print("Usage: breaker <path-to-data> <digit-write-path> <start-index> <end-index>")
		sys.exit(-1)

	path_to_data = args[1];
	digit_write_path = args[2];
	start_index = int(args[3]);
	end_index = int(args[4]);

	for idx in range(start_index, end_index + 1):
		file = path_to_data + "/" + str(idx) + ".jpeg"
		digit_list = separate_image(file)
		for j in range(6):
			print(idx)
			cv2.imwrite(digit_write_path + '/digit_' + str(idx) + '_' +  str(j) + '.jpeg', digit_list[j])

if __name__ == '__main__':
	divDigits(sys.argv)
