import http.client
import requests
import json
from lxml import etree


def get_courses(conn, category):
    url = f"/apix/soc/schedule/?category={category}&term=2238"
    # Make request to the API
    conn.request("GET", url)
    response = conn.getresponse()
    data = response.read()
    # print raw data --- testing purposes
    # print(data.decode("utf-8"))

    # Parse the JSON data
    parsed_data = json.loads(data)
    total_rows = parsed_data[0]["TOTALROWS"]
    remaining_rows = total_rows

    ''' BASIC LOOP - example demonstration purposes
    for i in range(len(parsed_data[0]["COURSES"])):
        print(parsed_data[0]["COURSES"][i]["name"])
        print([i])
    '''

    # Create an empty container (will be defined to more precise data structure later) to store the courses
    courses = []

    while True:
        for course in parsed_data[0]["COURSES"]:
            instructors_list = []
            # the set below is used to check for duplicate instructors across sections before adding to instructor_list
            instructors_set = set()
            credit_amount = ""
            for section in course["sections"]:
                credit_amount = section["credits"]
                for instructor in section["instructors"]:
                    name = instructor["name"]
                    if name not in instructors_set:
                        instructors_list.append(name)
                        instructors_set.add(name)
            course_data = {
                "name": course["name"],
                "code": course["code"],
                "credits": credit_amount,
                "instructors_list": instructors_list,
                # Add any other attributes to store here
            }
            courses.append(course_data)

        retrieved_rows = parsed_data[0]["RETRIEVEDROWS"]
        remaining_rows -= retrieved_rows
        if remaining_rows <= 0:
            break

        last_control_num = parsed_data[0]["LASTCONTROLNUMBER"]
        url = f"/apix/soc/schedule/?category={category}&term=2238&last-control-number={last_control_num}"

        # Make request to the API with the updated URL
        conn.request("GET", url)
        response = conn.getresponse()
        data = response.read()
        # Parse the JSON data again
        parsed_data = json.loads(data)

    return courses

def get_avgRating(profName):
    connection = http.client.HTTPSConnection("www.ratemyprofessors.com")
    url = f"/search/teachers?query={profName}&sid=1100"

    connection.request("GET", url)
    response = connection.getresponse()
    data = str(response.read())

    root = etree.HTML(data)[0]

    for child in root:
        if child.tag == 'script':
            if(child.text == None):
                continue
            else:
                index = child.text.find("avgRating")
                if index != -1:
                    index += 11
                    if child.text[index:index+1] == '0':
                        rating = 0.0
                    else:
                        rating = float(child.text[index:index+3])

    return rating


# Make the HTTP connection
connection = http.client.HTTPSConnection("one.ufl.edu")

# Get the courses for each category --- only humanities being demonstrated
humanities_courses = get_courses(connection, "CWSP&ge-h=true")
# Example looping and printing values for all humanities courses
# Print the courses
''' for course in humanities_courses:
    print(course["name"], course["code"], course["instructors_list"], course["credits"]) '''

genEdType = int(input(
    "What gen-ed requirement would you like to fulfill?\n" +
    "1. Biological Sciences\n" +
    "2. Composition\n" +
    "3. Diversity\n" +
    "4. Humanities\n" +
    "5. International\n" +
    "6. Mathematics\n" +
    "7. Physical Sciences\n" +
    "8. Social and Behavioral Sciences\n" +
    "Enter a number 1-8 corresponding to the above gen-ed category: "
))

numOfCredits = int(input("How many credits would you like your gen-ed class to be? "))

