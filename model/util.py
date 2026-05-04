import json
from typing import Optional, Union, Dict, List

def extract_json_object(text: str) -> Optional[Union[Dict, List]]:
    """
    Extracts the first valid JSON object (dict or list) found within a string.

    Args:
        text: The input string potentially containing a JSON object and other text.

    Returns:
        The parsed JSON object (as a dictionary or list) if found, otherwise None.
    """

    for i in range(len(text)):
        if text[i] in ['{', '[']:
            # Try to decode the substring starting from this character
            try:
                # Attempt to decode the rest of the string from this point
                # This works if the JSON is the last part of the string or
                # if subsequent characters are valid JSON/whitespace.
                result = json.loads(text[i:])

                if 'reasoning' and 'code' in result:
                    # If the JSON object contains 'reasoning' and 'code', return it
                    return result
            except json.JSONDecodeError as e:
                # If decoding the rest of the string fails, it might be because
                # there's extra text *after* the JSON object.
                # The error 'e' includes the position 'e.pos' where parsing stopped.
                # We can try to decode the substring *up to* that position.
                try:
                    # Slice the string from the potential start 'i' up to
                    # the position where the previous error occurred (i + e.pos)
                    substring = text[i : i + e.pos]
                    result = json.loads(substring)
                    if 'reasoning' and 'code' in result:
                        # If the JSON object contains 'reasoning' and 'code', return it
                        return result
                except json.JSONDecodeError:
                    pass # Continue the outer loop

    return None