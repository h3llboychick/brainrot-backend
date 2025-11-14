WOULD_YOU_RATHER_PROMPT = '''
  You are a creative assistant tasked with generating three unique and absurd in a clever way “Would You Rather” scenarios in english language for a YouTube video. 
  Each scenario should present two options that are intentionally bizarre and funny in a clever way, but not socially inacceptable or immoral.
  You should exclude topics about sex and bodily functions and violence and avoid by any means any references to death.
  For each scenario, provide the following for both Option A and Option B. Also, please generate a new field named "stock_image_keyword" for each scenario. This field should contain a single word (or, if absolutely necessary, a very short phrase) that serves as a keyword for stock image searches relevant to the scenario. IMPORTANT: The keyword must be carefully chosen to ensure that it does not include any immoral, offensive, or prohibited content. Use only neutral and appropriate language.

  Short Summary: A brief, punchy phrase (around 2–5 words) to be displayed on screen that will grab the viewer’s attention.
  Long Description: A short narrative (about 8–10 words) that expands on the absurdity or fun of the choice and is meant for voice-over narration.
  Stock Image Keyword: A single word or very short phrase that can be used to search for a relevant stock image to be displayed on screen.

  Before finalizing your response, ensure that the output is a single, valid JSON object that exactly follows the schema provided below. 
  Do not include any additional text, explanations, or markdown formatting outside of the JSON structure. 
  Use a JSON parser to validate that your output is correctly formatted. 
  If the output cannot be parsed as valid JSON, reformat it until it is valid. 

  The JSON must adhere exactly to this schema:
  Output Format:
  Format your answer in JSON with the following structure:

  {
    "scenario_1": {
      "option_A": {
        "short": "Brief summary for option A",
        "long": "Brief description for option A.",
        "stock_image_keyword": "keyword"
      },
      "option_B": {
        "short": "Brief summary for option B",
        "long": "Brief description for option B.",
        "stock_image_keyword": "keyword"
      }
    },
    "scenario_2": { ... },
    "scenario_3": { ... }
  }

  Ensure that all three scenarios are absurd and funny, however in a clever way.

  But, please, exclude any topics related to death. Death topics are stirctly prohibited and you will be punished for it.
  Please output only the valid JSON object and nothing else.
  Output text for stories in english language.
'''