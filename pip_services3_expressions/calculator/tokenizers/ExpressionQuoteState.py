# -*- coding: utf-8 -*-

from pip_services3_expressions.tokenizers.IQuoteState import IQuoteState
from pip_services3_expressions.tokenizers.Token import Token
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.utilities.CharValidator import CharValidator


class ExpressionQuoteState(IQuoteState):
    """
    Implements an Expression-specific quote string state object.
    """

    def __init__(self):
        super(ExpressionQuoteState, self).__init__()
        self.QUOTE = ord('"')

    def next_token(self, reader, tokenizer):
        """
        Gets the next token from the stream started from the character linked to this state.

        :param reader: A textual string to be tokenized.
        :param tokenizer: A tokenizer class that controls the process.
        :return: The next token from the top of the stream.
        """
        first_symbol = reader.read()
        token_value = ''
        token_value += chr(first_symbol)

        next_symbol = reader.read()
        while not CharValidator.is_eof(next_symbol):
            token_value += chr(next_symbol)
            if next_symbol == first_symbol:
                if  reader.peek() == first_symbol:
                    next_symbol = reader.read()
                    token_value += chr(next_symbol)
                else:
                    break
            next_symbol = reader.read()

        return Token(TokenType.Word if first_symbol == self.QUOTE else TokenType.Quoted, token_value)

    def encode_string(self, value, quote_symbol):
        """
        Encodes a string value.

        :param value: A string value to be encoded.
        :param quote_symbol: A string quote character.
        :return: An encoded string.
        """
        if value is None:
            return None
        quote_string = chr(quote_symbol)
        result = quote_string + value.replace(quote_string, quote_string + quote_string) + quote_string
        return result

    def decode_string(self, value, quote_symbol):
        """
        Decodes a string value.
        
        :param value: A string value to be decoded.
        :param quote_symbol: A string quote character.
        :return: An decoded string.
        """
        if value is None:
            return None

        if len(value) >= 2 and ord(value[0]) == quote_symbol and ord(value[-1]) == quote_symbol:
            quote_string = chr(quote_symbol)
            return value[1:-1].replace(quote_string + quote_string, quote_string)
        return value
