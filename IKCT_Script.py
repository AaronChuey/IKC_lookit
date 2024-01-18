import pandas as pd
import json

#----- Load JSON data -----#
with open('/Users/suzannahwistreich/Downloads/Which-wub-do-you-like-_all-responses-identifiable.json', 'r') as json_file:
    data = json.load(json_file)

# init spreadsheet rows
rows = []

# init list of participants to check for duplicates while processing
acceptedChildHashedIds = [] 

# pilot hashedIds
pilotHashedIds = []

#----- For each participant, extract desired fields from JSON data -----#
participantCount = 0
for response_entry in data:
    # if participant was collected AFTER pilot, include
    participantCount += 1
    # get participant ID
    childData = response_entry['child']
    hashedId = childData['hashed_id']

    # moves past pilot data if > 0
    if participantCount > 0:
        # checks to make sure participant was not in pilot and does not already have an accepted response
        if (hashedId not in acceptedChildHashedIds) and (hashedId not in pilotHashedIds):
            # getting desired frames
            responseData = response_entry['response']
            conditionData = responseData['conditions'][0]
            expData = response_entry['exp_data']
            
            # checking for a completed response, then getting info needed
            if '12-trial-segment' in expData:
                trialSegment = expData['12-trial-segment']

                # adding all desired data to this participant row
                row = [
                    hashedId,
                    str(responseData['date_created']),
                    childData['age_rounded'],
                    childData['gender'],
                    "prefail" if str(conditionData['parameterSet']['VIDEO']).find("prefail") != -1 else "postfail",
                    conditionData['parameterSet']['VIDEO'],
                    conditionData['parameterSet']['DV-VIDEO'],
                    "sneeze" if str(conditionData['parameterSet']['VIDEO']).find("sneeze") != -1 else "speech",
                    "",
                    "",
                    response_entry['participant']['hashed_id'],
                    ""
                ]
                rows.append(row)
                # add childHashedId to master list
                acceptedChildHashedIds.append(hashedId)
    # adds pilot ids to list to check against other responses
    else:
        pilotHashedIds.append(hashedId)

# Define column headers
columns = [
    'child__hashed_id',
    'response__date_created',
    'child__age_rounded',
    'child__gender',
    'video_type',
    'video_watched',
    'wub_order',
    'condition',
    'knowledge',
    'included',
    'parent__hashed_id',
    'notes'
]

# Create a DataFrame
dfUnsorted = pd.DataFrame(rows, columns=columns)
        
#----- sort by speech/sneeze condition, then response date -----#
df = dfUnsorted.sort_values(['condition', 'response__date_created'], ascending = [False, True])

#----- Write DataFrame to an Excel file -----#
output_file = '~/Desktop/IKCT datasheet.xlsx'
df.to_excel(output_file, index=False)
print(f"Data has been written to {output_file}")
print(f"Total Participants without Pilot: {len(acceptedChildHashedIds)}")
