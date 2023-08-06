"""Shared functions."""

def is_int(string):
    """Returns True if int(string) doesn't fail, otherwise false.

    Arguments:
        string {str} -- string to test

    Returns:
        bool -- Can string be converted into an int?

    """
    try:
        int(string)
        return True
    except ValueError:
        return False


# Keep trying user input until condition is met
def retry_valid_input(
        prompt,
        title='',
        default=None,
        condition=lambda x: x is not None,
        transform=lambda x: x):
    """Keep asking user for input until user input satifies *condition* function.

    Arguments:
        prompt {str} -- User prompt text.

    Keyword Arguments:
        title {str} -- Name of this request for information. (default: {''})
        default {Any} -- Default value of user input. Be careful that default
                         passes condition. (default: {None})
        condition {function: a -> bool} --
                Condition returning boolean to signal correct input from user.
                (default: {lambdax:x is not None})
        transform {function: a -> b} --
                Transformation function transforming user data
                before returning it. (default: {lambda x:x})

    Returns:
        b -- Returns result of transform function (defaults to identity)

    """
    if default is not None:
        prompt += ' [{}] '.format(default)
    while True:
        user_input = raw_input(prompt) or default
        # If user_input passes the condition, transform and save the output
        if condition(user_input):
            break
        else:
            print('Invalid {}'.format(title))
    return transform(user_input)