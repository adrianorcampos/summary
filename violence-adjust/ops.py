import numpy as np

_THRESHOLDS = [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75]


# helper function to calculate IoU
def iou2(box1, box2):
    x11, y11, x12, y12 = box1

    x21, y21, x22, y22 = box2[:4]
    w1 = np.int64(x12 - x11)
    h1 = np.int64(y12 - y11)
    w2 = np.int64(x22 - x21)
    h2 = np.int64(y22 - y21)

    assert w1 * h1 > 0
    assert w2 * h2 > 0
    x12, y12 = x11 + w1, y11 + h1
    x22, y22 = x21 + w2, y21 + h2

    area1, area2 = w1 * h1, w2 * h2
    xi1, yi1, xi2, yi2 = max([x11, x21]), max([y11, y21]), 
        min([x12, x22]), min([y12, y22])

    if xi2 <= xi1 or yi2 <= yi1:
        return 0.0
    else:
        intersect = (xi2 - xi1) * (yi2 - yi1)
        union = area1 + area2 - intersect
        return intersect / union


def iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    # compute the area of both the prediction and ground-truth rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou



def map_iou(boxes_true, boxes_pred, scores=[], thresholds=_THRESHOLDS):
    """
    Mean average precision at differnet intersection over union (IoU) threshold
    
    input:
        boxes_true: Mx4 numpy array of ground true bounding boxes of one image. 
                    bbox format: (x1, y1, w, h)
        boxes_pred: Nx4 numpy array of predicted bounding boxes of one image. 
                    bbox format: (x1, y1, w, h)
        scores:     length N numpy array of scores associated with predicted bboxes
        thresholds: IoU shresholds to evaluate mean average precision on
    output: 
        map: mean average precision of the image
    """
    
    # According to the introduction, images with no ground truth bboxes will not be 
    # included in the map score unless there is a false positive detection (?)
    
    # The metric sweeps over a range of IoU thresholds
    if not thresholds: return 0
        
    # return None if both are empty, don't count the image in final evaluation (?)
    # if len(boxes_true) == 0 and len(boxes_pred) == 0: return None
    # assert boxes_true.shape[1] == 4 and boxes_pred.shape[1] == 4
    # if len(boxes_pred):
    if scores:
        assert len(scores) == len(boxes_pred), "boxes_pred and scores should be same length"
        # sort boxes_pred by scores in decreasing order
        boxes_pred = boxes_pred[np.argsort(scores)[::-1], :]
    
    map_total = 0
    
    # loop over thresholds
    for t in thresholds:
        matched_bt = set()
        tp, fn = 0, 0
        for i, bt in enumerate(boxes_true):
            matched = False
            for j, bp in enumerate(boxes_pred):
                miou = iou(bt, bp)
                if miou >= t and not matched and j not in matched_bt:
                    matched = True
                    tp += 1 # bt is matched for the first time, count as TP
                    matched_bt.add(j)

	    if not matched:
                fn += 1    # bt has no match, count as FN
                
        fp = len(boxes_pred) - len(matched_bt)   # FP is the bp that not matched to any bt
        m = tp / float((tp + fn + fp))
        map_total += m
    
    return float(map_total) / len(thresholds)

if __name__ == '__main__':
    bA = [596, 431, 929, 638]
    bB = [703, 461, 846, 592, 0.444396]
    result = iou(bA, bB)
    print result
