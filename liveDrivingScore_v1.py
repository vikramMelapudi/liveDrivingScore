liveDriveScoreConfigs = None

def getDrivingScore(spec, curDistance, curMileage, curPtrTimes=dict(), curIncidenceCounts=dict()):
  # make = txt for now, alter move to specID
  # curDistance = distance travelled so far in km
  # curMileage = mileage so far in kmpl
  # curPtrTime = {'below':cnt in ms, 'in':cnt in ms, 'above':cnt in ms}
  # curIncidenceCounts = {'incidence1':counts, 'incidence2':counts ....]
  # x`
  # returns {'score':score, 'metat': {..}} score is a float in [0,4] range
  from datetime import datetime
  global liveDriveScoreConfigs

  if liveDriveScoreConfigs is None:
    print('load config data first')
    return None
  
  scoreMetricsWt = {'mileage': 1.0, "ptr.below":-0.5}
  
  # get config by make
  config = liveDriveScoreConfigs['default']
  refSpec = 'default'
  if spec in liveDriveScoreConfigs:
    config = liveDriveScoreConfigs[spec]
    refSpec = spec
  # get config by distance
  distConfig  = config[-1]
  for distConfig in config:
    if curDistance<distConfig['distance']:
      break
      
  metrics = {}
  
  # get Score for ptr
  ptrTimesTotal = 0
  for k in curPtrTimes:
    ptrTimesTotal += curPtrTimes[k]
  for k in curPtrTimes:
    metrics[k] = curPtrTimes[k]/ptrTimesTotal;
  metrics['mileage'] = curMileage
  
  scores = {}
  totalScore = 0 
  norm = 0
  for metric in scoreMetricsWt:
    score = 0
    value = metrics[metric]
    # get bin# as score
    for q in range(len(distConfig[metric])):
      if value>distConfig[metric][q][1]:
        score = q+1
    # get float score to account for pts between bin (linear interpolation)
    if score>0 and score<len(distConfig[metric]):
        offst = (value-distConfig[metric][score-1][1])/(distConfig[metric][score][1]-distConfig[metric][score-1][1])
        score += offst
    # reverse score (when lower is better)    
    if scoreMetricsWt[metric]<0:
        score = 5.0 - score
    scores[metric] = round(score,2)
    totalScore += score*abs(scoreMetricsWt[metric])
    norm += abs(scoreMetricsWt[metric])
  finalScore = totalScore*1.0/norm
  scoreInfo = {'score':finalScore, 
               'meta': {'scores':scores, 'refSpec': refSpec, 'time':datetime.now().timestamp()}
               }
  
  return scoreInfo 

if __name__ == '__main__':
    import json
    import pandas as pd

    liveDriveScoreConfigs = json.load(open('configLiveDriveScore.json','r'))


    testData2 = pd.read_csv('test/testDataLiveScore.csv')

    ntest = 0
    results = []
    for n in range(len(testData2)):
        ent = testData2.iloc[n]
        spec = ent['spec']
        dist = ent['dist']
        mileage = ent['mileage']
        ptrs = ent[['ptr.below','ptr.in','ptr.above']]
        ptrs = ptrs.to_dict()
        score = getDrivingScore(spec, dist, mileage, ptrs)
        ntest += 1
    
        info = {'liveScore': score['score'], 'refSpec': score['meta']['refSpec'], 'disst':dist, 'mileage':mileage, 'ptr.below':ptrs['ptr.below'], 'spec':spec}
        results.append(info)
    results = pd.DataFrame(results)
    results.to_csv('test/test_output.csv')
