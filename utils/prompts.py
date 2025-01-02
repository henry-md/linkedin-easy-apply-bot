test_prompt = "Say hi!"

specify_json_output_prompt_format = """
I'm going to give you a list of form elements from a Linkedin job posting, in text format. I want your response to be in JSON format, so that I can pass your entire response into JSON.parse(), and have my code not break. 

I want your json object response to have the following structure: it should be a list with length equal to the number of elements I pass in - one list item per element. Each list item should be an object, with some or none of the following optional properties: 'click', 'text', 'option'. The object should contain only those properties (case sensitive, exactly as written), and no other property. (1) Click will have a boolean value which represents whether or not it should be clicked. (2) Text will have a string value which represents the text that should be typed into the element. Feel free to leave the value as an empty string for non-input elements, or input elements which are not required and for which you do not want to respond, or  input elements which have a default value that is already good that we don't want to change (these may be auto-filled from previous applications). (3) Option will have a string value which represents the option that should be selected from the dropdown. Feel free to leave the value as an empty string if the element isn't a dropdown. If you do select a value, make sure to write it in option character for character, case sensitive.

Please note that these form elements are text representations taken from a scanning of the website, so you may get a label before or after it's radio elements, but the label will most commonly be before the radio elements, and they will never be separated by other elements in between. In other words, you can be sure the first question and first selection/radio buttons/etc. are the first question.

I will now give a sample input, sample output (what I expect you to return), and a brief commentary.

Sample Input:
Element 1: HTML Tag: span; Inner Text: Have you completed the following level of education: Bachelor's Degree?; Required: True; 
Element 2: HTML Tag: label; Inner Text: Yes; 
Element 3: HTML Tag: label; Inner Text: No;

Element 4: HTML Tag: label; Inner Text: How many years of work experience do you have with 3D Printing?; Required: True; 
Element 5: HTML Tag: input (Type: text); Default Value: ''; 
Warning (element 6): Enter a whole number between 0 and 99

Element 7: HTML Tag: label; Inner Text: How many years of work experience do you have with CAD/CAM Software?; Required: True; 
Element 8: HTML Tag: input (Type: text); Default Value: ''; 
Warning (element 9): Enter a whole number between 0 and 99

Element 10: HTML Tag: label; Inner Text: How many years of work experience do you have with Javascript?; Required: True; 
Element 11: HTML Tag: input (Type: text); Default Value: ''; 
Warning (element 12): Enter a whole number between 0 and 99

Element 13: HTML Tag: span; Inner Text: Are you comfortable commuting to this job's location?; Required: True; 
Element 14: HTML Tag: label; Inner Text: Yes; 
Element 15: HTML Tag: label; Inner Text: No; 
Warning (element 16): Please make a selection

Element 17: HTML Tag: label; Inner Text: Do you have experience qualifying metal parts created via additive manufacturing?; Required: True; 
Element 18: HTML Tag: select; Default Value: 'Select an option'; Options: ['Select an option', 'Yes', 'No']; 
Warning (element 19): Please enter a valid answer

Sample Output:
[
  {},
  { "click": true },
  {},

  {},
  {"text": "0"},
  {},

  {},
  {"text": "0"},
  {},

  {},
  {"text": "4"},
  {},
  
  {},
  { "click": true},
  {},
  {},

  {},
  { "option": "No"},
  {},
]

Commentary on the example:
Note that I put two returns at times to differentiate questions on the input and output, but you will not have this luxury on the actual input. The first 3 elements are about whether I've completed my Bachelor's Degree. The next 3 are about how many years I have with 3d printing. The warning message lets me know that the answer should be in the form of a whole number. This should be 0 since anything else would be unrealistic given my background. The next 3 are about how many years I have with CAD/CAM software; next 3 are about Javascript; Next 4 are about whether I'm comfortable commuting to the job's location; Next 3 are about whether I have experience qualifying metal parts created via additive manufacturing. As you can see, the response contains 19 elements, one for each form element (warnings count as elements too). Note that it is enough to write an option or text — you do not need to click something if you specify a text or option.

So I've just gone over the format your response should take. I will now give you specific information that will help you choose the content of your response.

Please make a determination as to the number of years I could have worked on the given technology, charitably, based on the work experience in my resume. While I would like you to be charitable in terms of years, I do not want you to say anything that is verifiably false. For example, it would be easy to verify that I do not have a masters, and it is easy to verify the particular companies I've worked for. However, it would not be easy to verify whether or not I've used a ticketing technology like Jira — since I have around 3 years of work experience listed on my resume, you may write that I have 2 years of work experience in Jira.

For logistical questions, choose the most “vanilla” response that keeps me in running for the job. For example, if they ask whether I live in a place like North Korea, etc. and am seeking refuge, you should bias towards the more likely response (no, in this case).

Do not fill in information that is not required.

Now some info about my work experience:
"""

# [maybe add info about me here, or elsewhere]
personal_info_prompt = """
I am a senior at Johns Hopkins University, expected to graduate in May 2025. I have a BS in Computer Science. I'm a white male but would prefer not to specify my race or gender. I'm not a disabled veteran or anything unusual.

I have 4 years of work experience in Python, Javascript, Typescript.
I have 3 years of experience in React, Node.js, Express.js, MongoDB, Next.js, Tailwind, SEO, HTML, CSS, Git, GitHub, Unix/Linux.
I have 2 years of experience in AWS DevOps including Amplify & EC2, Java, SQL.
I have 1 year of experience in C++, Docker, Dash, PyTorch

As a KnoWhiz intern, I developed full-stack features for 1.1v of the LLM-based AI Learning platform with personalized courses. I led development of full stack features, including Quizlet import feature enabling users to transform Quizlet sets into native KnoWhiz flashcard sets; developed landing page and led SEO track. I designed and implemented RESTful APIs in Java to fetch and serve data to the Typescript and Redux front-end. I mentored a junior front-end developer in React & Typescript. I helped with bug fixes, learning resources, pull requests, etc.

As a Helpful intern, I led development of an internal platform that allows other devs to work on open projects requiring technical expertise. I contributed to the in-house UI library by implementing Figma designs as React components and web pages with AWS Amplify. I developed dashboard page, sign-up, sign-in pages from scratch for their 2.0 website. I proactively researched and evaluated alternative tooling for Figma-to-frontend development workflows including AWS Amplify, Figma plugins, and Cursor.ai. I delivered presentation to software engineering teams across Helpful.

As a NIST intern, I developed a Python and SQL backend and Dash frontend, implementing 2-week agile sprints with Scrum practices. I led revision of SQL database for uploading broader data, and of Dash UI to support text queries and more video analysis features. I integrated transformer-based deep neural network model in back-end to run data science analyses of structured audio data.
"""