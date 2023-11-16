import pandas as pd
import json

#----- Load JSON data -----#
with open('/Users/suzannahwistreich/Desktop/Which-wub-do-you-like-_all-responses-identifiable.json', 'r') as json_file:
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

    # moves past pilot data
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
                    str(int(childData['age_rounded']) / 365)[:1],
                    childData['age_rounded'],
                    childData['gender'],
                    childData['condition_list'],
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
    'age_years',
    'child__age_rounded',
    'child__gender',
    'child__condition_list',
    'wub.order',
    'condition',
    'knowledge',
    'included',
    'parent__hashed_id',
    'notes'
]

# Create a DataFrame
dfUnsorted = pd.DataFrame(rows, columns=columns)

#----- add empty rows to spreadsheet if a given category (age and condition) isn't filled yet -----#
ages = ["0", "1", "2"]
conditions = ["speech", "sneeze"]
target = 36

# iterate through age/condition combinations
for age in ages:
    for condition in conditions:
        age_category = dfUnsorted['age_years'] == age
        condition_category = dfUnsorted['condition'] == condition
        combined_category = age_category & condition_category
        count = combined_category.sum()
        # if there are not enough responses for this combination, pad spreadsheet with empty rows
        if count < target:
            row = ["", "~Place Holder", age, "", "", "", "", condition, "", "", "", ""]
            rowsToAdd = [row] * (target - count)
            dfAdd = pd.DataFrame(rowsToAdd, columns=columns)
            dfUnsorted = pd.concat([dfAdd, dfUnsorted])
        
#----- sort by age, then speech/sneeze condition, then response data -----#
df = dfUnsorted.sort_values(['age_years', 'condition', 'response__date_created'], ascending = [True, False, True])

#----- Write DataFrame to an Excel file -----#
output_file = '~/Desktop/IKCT datasheet.xlsx'
df.to_excel(output_file, index=False)
print(f"Data has been written to {output_file}")
print(f"Total Participants without Pilot: {len(acceptedChildHashedIds)}")
