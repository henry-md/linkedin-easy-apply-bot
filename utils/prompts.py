test_prompt = "Say hi!"

specify_json_output_prompt_format = """
I'm going to give you a list of form elements from a Linkedin job posting, in text format. I want your response to be in JSON format, so that I can pass your entire response into JSON.parse(), and have my code not break. 

I want your json object response to have the following structure: it should be a list with length equal to the number of elements I pass in - one list item per element. Each list item should be an object, with the following properties: 'click', 'text', 'option'. (1) Click will have a boolean value which represents whether or not it should be clicked. (2) Text will have a string value which represents the text that should be typed into the element. Feel free to leave the value as an empty string for non-input elements, or input elements which are not required and for which you do not want to respond, or  input elements which have a default value that is already good that we don't want to change (these may be auto-filled from previous applications). (3) Option will have a string value which represents the option that should be selected from the dropdown. Feel free to leave the value as an empty string if the element isn't a dropdown. If you do select a value, make sure to write it in option character for character, case sensitive.

Please note that these form elements are text representations taken from a scanning of the website, so you may get a label before or after it's radio elements, but the label will most commonly be before the radio elements, and they will never be separated by other elements in between. In other words, you can be sure the first question and first selection/radio buttons/etc. are the first question.

I will now give a sample input, sample output (what I expect you to return), and a brief commentary.

Sample Input:
Element 1: HTML Tag: span; Inner Text: Have you completed the following level of education: Bachelor's Degree?; Required: True; 
Element 2: HTML Tag: label; Inner Text: Yes; 
Element 3: HTML Tag: label; Inner Text: No; 
Element 4: HTML Tag: span; Inner Text: Are you comfortable working in an onsite setting?; Required: True; 
Element 5: HTML Tag: label; Inner Text: Yes; 
Element 6: HTML Tag: label; Inner Text: No; 
Element 7: HTML Tag: label; Inner Text: Are you legally authorized to work in the United States? And will you now, or in the future, NOT require sponsorship for employment visa?; Required: True; 
Element 8: HTML Tag: select; Default Value: Select an option; Options: ['Select an option', 'Yes', 'No']; 
Element 9: HTML Tag: label; Inner Text: Are you available for relocation across USA? As the paid orientation & induction will be at Atlanta, Georgia and project location will be anywhere in US?; Required: True; 
Element 10: HTML Tag: select; Default Value: Select an option; Options: ['Select an option', 'Yes', 'No'];

Sample Output:
[
  {
    "click": false,
    "text": "",
    "option": ""
  },
  {
    "click": true,
    "text": "",
    "option": ""
  },
  {
    "click": false,
    "text": "",
    "option": ""
  },
  {
    "click": false,
    "text": "",
    "option": ""
  },
  {
    "click": true,
    "text": "",
    "option": ""
  },
  {
    "click": false,
    "text": "",
    "option": ""
  },
  {
    "click": false,
    "text": "",
    "option": ""
  },
  {
    "click": false,
    "text": "",
    "option": "Yes"
  },
  {
    "click": false,
    "text": "",
    "option": "No"
  },
  {
    "click": true,
    "text": "",
    "option": "Yes"
  }
]

Commentary on the example:
The first 3 elements are the first question, and yes, I've completed by Bachelors (so I would want to click the element that corresponds to the 'yes' button for that question). Elements 4 to 6 are about whether I'm comfortable working onsite, and I am. Elements 7 to 8 are about whether I'm legally authorized to work in the United States, and I am (so I would want to select the 'yes' option from the dropdown corresponding to that question). Elements 9 and 10 are about whether I'm available for relocation across the United States, and I am.
"""

# [maybe add info about me here, or elsewhere]