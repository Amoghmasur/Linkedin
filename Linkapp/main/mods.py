def subparts(data, target, info):

    '''Here, two lists are created: person_topics and company_topics. 
    These lists contain predefined topics related to a person's profile 
    and a company's profile, respectively.'''

    person_topics = ['About', 'Experience', 'Education', 'Projects', 'Skills', 'Interests', 'People also viewed',
                     'You might like', 'Pages for you', 'Recommendations', 'People you may know']
    company_topics = ['Overview', 'Website', 'Industry', 'Company size', 'Headquarters', 'Founded', 'Specialties']
    subarr = [] # An empty list named subarr is created. This list will be used to store specific parts of the data list

    '''This part tries to find the index of a specific target element in the data list.
      If the target is not found (ValueError), it returns a list containing a message 
      indicating that the information is not available.'''
    
    try: 
        ind = data.index(target) + 1
    except ValueError:
        return ["**    Not Available    **"]

    topics = ''
    #Depending on the value of info, it assigns the appropriate list of topics (person_topics or company_topics) 
    # to the variable topics.
    if info == 'person':
        topics = person_topics
    elif info == 'company':
        topics = company_topics

        '''This loop runs indefinitely (until explicitly broken). 
        It iterates through the data list starting from the index obtained earlier (ind).
          It stops if the end of the data list is reached or if the current element is in the list of topics. 
          It appends the current element to the subarr list and increments the index.'''
        
    while True:
        if ind >= len(data):
            break
        if data[ind] in topics:
            break
        subarr.append(data[ind])
        ind += 1

    return subarr # the function returns the list subarr containing the specific parts of the data list.


