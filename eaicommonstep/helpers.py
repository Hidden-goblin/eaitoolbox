# -*- coding: utf-8 -*-
import dpath
import logging
from copy import deepcopy
from time import sleep

log = logging.getLogger(__name__)

ATTRIBUTE_LIST = ("user",
                  "search",
                  "to_be_entry",
                  "current_entry",
                  "collection",
                  "consignment",
                  "despatch_options",
                  "recipient",
                  "sender",
                  "importer",
                  "exporter",
                  "return_data")


def parse_true_false(value: str = None):
    """
    Return the boolean value related to the string value.

    Remember 'false' is True
    :param value: the input string
    :raise Exception: the input string is neither 'true' or 'false' case insensitive
    :return: Boolean
    """
    if value.casefold() == "false".casefold():
        return False
    elif value.casefold() == "true".casefold():
        return True
    else:
        raise Exception("value '{}' can't be checked as True or False".format(value))


def execute_postponed_actions(context, is_data: bool = True, actions_switcher: dict = None):
    """
    Execute postponed actions
    :param actions_switcher: the automaton list of actions which can be postponed
    :param context: the current context
    :param is_data:  boolean, True means set only data, False means execute actions (use models)
    :return: None
    """
    log.debug("postponed_action")

    if is_data:
        #  Do settings
        log.debug("is data statement")
        key_list = set(ATTRIBUTE_LIST).intersection(context.pre_conditions["postponed"].keys())
        for key in key_list:
            log.debug("Key : {}".format(str(key)))
            while context.pre_conditions["postponed"][key]:
                log.debug("Context.pre_conditions[postponed][key]: {} ".format(
                    context.pre_conditions["postponed"][key]))
                elem = context.pre_conditions["postponed"][key].pop(0)
                log.debug("elem contains: {}".format(elem))
                try:
                    # Check the path exist
                    if dpath.search(context.pre_conditions[key], elem["path"]):
                        dpath.set(context.pre_conditions[key],
                                  elem["path"],
                                  elem["value"])
                    else:
                        # Create a new entry
                        dpath.new(context.pre_conditions[key],
                                  elem["path"],
                                  elem["value"])
                except AssertionError as assertion:
                    log.error("Update data failed.\n '{}'".format(assertion.args[0]))
                    raise_exception(AssertionError,
                                    "Update data failed.\n '{}'".format(assertion.args[0]),
                                    context.evidence_folder)
                log.debug("pre_conditions : {}".format(str(context.pre_conditions[key])))
    else:
        #  Do execute steps
        log.debug("else statement")
        postponed_actions = deepcopy(context.pre_conditions["postponed"]["execution"])
        context.pre_conditions["postponed"]["execution"].clear()
        for index, action in enumerate(postponed_actions):
            log.debug("Index: {}, action: {}".format(index, action))
            if isinstance(action, str):
                context.execute_steps(action)
            elif isinstance(action, tuple) and len(action) == 2:
                log.debug("action switcher: {}".format(action))
                actions_switcher[action[0]](**action[1])
                sleep(0.5)
            else:
                raise Exception("Unknown action to process.\n"
                                "Get '{}'".format(repr(action)))

    log.debug("End of postponed_action ")


def set_model(context, switcher):
    """
    Set the correct model for the action
    :param switcher: the list of action--method dictionary
    :param context: the current context, switcher: action name
    :return: None
    """

    context.model.evidence_folder = context.evidence_folder
    # Execute postponed actions
    # Set data
    execute_postponed_actions(context, True, switcher)

    for element_context in context.pre_conditions:
        if element_context in ATTRIBUTE_LIST \
                and context.pre_conditions[element_context] is not None:
            setattr(context.model, element_context, context.pre_conditions[element_context])
            log.debug("context.model.{} : {}".format(
                element_context,
                getattr(context.model, element_context)))
    # Execute actions
    execute_postponed_actions(context, False, switcher)


def table_to_dictionary(table, key_field):
    result = dict()
    assert key_field in table.headings, \
        "key_field '{}' is not in the table headers".format(key_field)
    for row in table.rows:
        key = ""
        dictionary_part = dict()
        for element in table.headings:
            if element == key_field:
                key = row[element]
            else:
                dictionary_part[element] = row[element]
        result[key] = dictionary_part

    return result


def assert_return_message(response, code, message):
    assert isinstance(response, dict)
    assert all([key in response for key in ("code", "message", "value")])
    assert response["message"] == message, "Expected '{}'. Current:'{}'".format(message,
                                                                                response["message"])
    assert response["code"] == code, "Expected '{}'. Current:'{}'".format(code,
                                                                          response["code"])


def raise_exception(exception, message, evidence_folder):
    with open("{}/failure_message.txt".format(evidence_folder), "w+") as file:
        file.write(message)

    raise exception(message) from None


def my_path(my_dictionary: dict = None, path=None, value=None):
    items = path.split('/')
    # if the last character is a digit
    if items[-1].isdigit():
        items.pop()
        new_path = "/".join(items)
        # Check the element before the digit is already in the dictionary
        if dpath.search(my_dictionary, new_path):
            # Is it a list ?
            if isinstance(dpath.get(my_dictionary, new_path), list):
                dpath.new(my_dictionary,
                          path,
                          value)
            else:
                raise ValueError("The following entry can not be added: {}. "
                                 "This is not a list".format(my_dictionary[items[-2]]))
        # Not in the dictionary
        else:
            dpath.new(my_dictionary, new_path, [])
            dpath.new(my_dictionary, path, value)
    else:
        if dpath.search(my_dictionary, path):
            # Set the new value
            dpath.set(my_dictionary,
                      path,
                      value)
        else:
            dpath.new(my_dictionary,
                      path,
                      value)
    return my_dictionary


def provider_to_string(provider_value: object = None) -> str:
    if isinstance(provider_value, bool):
        return str(provider_value).lower()
    elif provider_value is None:
        return ''
    else:
        return str(provider_value)
