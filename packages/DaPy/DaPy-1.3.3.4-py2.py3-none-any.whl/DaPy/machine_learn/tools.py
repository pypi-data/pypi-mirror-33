from DaPy import mat, Frame

def score_clf(clf, X, Y, cutpoint=0.5):
    X, Y = mat(X), mat(Y)
    total = len(X)
    TP, FN, FP, TN = 0, 0, 0, 0
    
    mypredict = clf.predict(X)
        
    for predict, true in zip(mypredict, Y):
        try:
            answer = predict[0]
        except IndexError:
            answer = predict
            
        if answer > cutpoint:
            if true[0] == 1:
                TP += 1
            else:
                FP += 1
        else:
            if true[0] == 1:
                FN += 1
            else:
                TN += 1
                
    return Frame([
        ['Actual Positive', TP, FN, TP + FN],
        ['Actual Negative', FP, TN, FP + TN],
        ['Total', TP + FP, FN + TN, total]],
        ['', 'Predict Positive', 'Predict Negative', 'Total'])
    
