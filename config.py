FROM_PROJECT_ID = '3980'
TO_PROJECT_ID = '3977'
FROM_PROJECT = 'cc-30-rng/cc30-sicbo-' + FROM_PROJECT_ID
TO_PROJECT = 'cc-30-rng/cc30-sicbo-james-bond-' + TO_PROJECT_ID
USER_DEFINE_TYPE = ['BigEyeRoadAnalyticItem'+FROM_PROJECT_ID,
                    'DishRoadAnalyticItem'+FROM_PROJECT_ID,
                    'ScoreRoadAnalyticItem'+FROM_PROJECT_ID,
                    'statisticAnalyticItem'+FROM_PROJECT_ID,
                    'BigRoadAnalyticItem'+FROM_PROJECT_ID]
#Warning
# 1. All png, jpeg will auto add type 'sprite-frame', scale-9 not cloned