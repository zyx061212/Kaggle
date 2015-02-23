#!/usr/bin/env python



from sklearn import cross_validation

import math
from sklearn.ensemble import GradientBoostingRegressor

import numpy as np
import pandas as pd


import gc

import datetime
from sklearn.metrics import mean_squared_error

    
def run_stack(SEED, col, alpha):

    dset = "2"

    trainBaseTarget = pd.read_csv('../preprocess/pre_shuffled_target_' + col + '.csv')

    trainBase = pd.read_csv('../preprocess/pre_shuffled_train' + dset + '.csv')
    trainBase.drop(['PIDN'], axis=1, inplace=True)


    columns = trainBase.columns.values.tolist()
    columnsHighScore = trainBase.columns.values.tolist()


    print(trainBase.columns)
    
    trainBase = np.nan_to_num(np.array(trainBase))
    targetBase = np.nan_to_num(np.array(trainBaseTarget))
    #test = np.nan_to_num(np.array(test))
    
    gc.collect()   
   
    
    avg = 0
    avgLast = 1
    NumFolds = 5 


    clf = GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=1000, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False)

    
    
    
    print ("Data size: " + str(len(trainBase)))
    print("Begin Training")
    
    lenTrainBase = len(trainBase)
   

    gc.collect()
    
    
    featuresRemaining = []
    avgScore = []    
    
    
    while True:
        
        
     
        
        #print(clf)
        avg = 0
    
        coef_dataset = np.zeros((len(columns),NumFolds))
   
        foldCount = 0

        Folds = cross_validation.KFold(lenTrainBase, n_folds=NumFolds, indices=True)
            
        for train_index, test_index in Folds:
    
            #print()
            #print ("Iteration: " + str(foldCount))
            
            
            now = datetime.datetime.now()
            #print(now.strftime("%Y/%m/%d %H:%M:%S"))    
    
    
            target = [targetBase[i] for i in train_index]
            train = [trainBase[i] for i in train_index]

            
            targetTest = [targetBase[i] for i in test_index]    
            trainTest = [trainBase[i] for i in test_index]    

            

            #print "LEN: ", len(train), len(target)
            
            
            target = np.array(np.reshape(target, (-1, 1)) )           

            targetTest = np.array(np.reshape(targetTest, (-1, 1)) )  
            
            

            #clf.fit(train, target, sample_weight = weight
            clf.fit(train, target)
            predicted = clf.predict(trainTest) 
 
  
            print(str(math.sqrt(mean_squared_error(targetTest, predicted))))
            avg += math.sqrt(mean_squared_error(targetTest, predicted))/NumFolds

                 
            coef_dataset[:, foldCount] = clf.feature_importances_                

            foldCount = foldCount + 1
        

   
        
        coefs = coef_dataset.mean(1)        
        sorted_coefs = sorted(map(abs, coefs)) # must start by removing coefficients closest to zero.
        #print(coefs)
        print("len coefs: " + str(len(sorted_coefs)))
        if len(sorted_coefs) < 10 :
            break
        
        
        threshold = 0.0
        if len(sorted_coefs) > 10000:         
            threshold = sorted_coefs[10000]
        elif len(sorted_coefs) > 100:         
            threshold = sorted_coefs[50]
            clf = GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=3000, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False)
        elif len(sorted_coefs) > 50:         
            threshold = sorted_coefs[5]
            clf = GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=5000, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False)
        else:
            threshold = sorted_coefs[2]
            clf = GradientBoostingRegressor(loss='ls', learning_rate=0.1, n_estimators=5000, subsample=1.0, min_samples_split=2, min_samples_leaf=1, max_depth=3, init=None, random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None, warm_start=False)



        print(str(len(columns)))
        print(trainBase.shape)
        
        toDrop = []        
        
        # hey, cannot drop var11 and id columns          
        for index in range(len(coefs) - 1, -1, -1): # must reverse columns all shift to lower numbers.
            if  abs(coefs[index]) <= threshold and columns[index] != "PIDN":# abs(), remove closest to zero.
                #print("Drop: " + str(index) + " " + columns[index] + " " + str(coefs[index]))
                #trainBase = np.delete(trainBase,[index], axis=1)
                toDrop.append(index)
               
               
                #print(columns)
                if columns[index] in columns: 
                    columns.remove(columns[index])  
                #print(columns)
        
        #print("start drop")
        trainBase = np.delete(trainBase,toDrop, axis=1)      
        #print("End drop")        
        
        
        if avg < avgLast:
            print("Saving Copy " + str(avgLast) + " " + str(avg))
            avgLast = avg
            columnsHighScore = columns.copy()

        print("Threshold: " + str(threshold))        
        print ("------------------------Average: " + str(avg))
        #print(columnsHighScore)
        #print(str(len(columns)))
        #print(trainBase.shape)
           
           
        featuresRemaining.append(len(columns))           
        avgScore.append(avg)
           
        #break
    
    
    columnsHighScore.insert(0, 'PIDN')    # add back to be sure it ends up in final model.
    
               
    gc.collect()    
    trainBase = pd.read_csv('../preprocess/pre_shuffled_train' + dset + '.csv')
    trainBase = trainBase.loc[:,columnsHighScore]
    trainBase.to_csv("../models/gbX" + dset + "_train_" + col + ".csv", index = False)
    
    
    gc.collect()
    test = pd.read_csv('../preprocess/pre_shuffled_test' + dset + '.csv')
    test = test.loc[:,columnsHighScore] 
    test.to_csv("../models/gbX" + dset + "_test_" + col + ".csv", index = False)  
      
      
    print(columnsHighScore)      
    print(featuresRemaining)
    print(avgScore)
    
    
if __name__=="__main__":
    
    colsTarget = ['Ca','P','pH','SOC','Sand']     
    #colsTarget = ['Sand']   
    alphas = [0.00961077966238,0.0356224789026,0.00621016941892,0.0148735210729,0.00961077966238]  
    #alphas = [0.000452035365636]  

    for Index, col in enumerate(colsTarget):
        run_stack(448, col, alphas[Index])
