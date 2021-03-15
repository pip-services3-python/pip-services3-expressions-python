# -*- coding: utf-8 -*-

from abc import ABC

from pip_services3_expressions.io.IScanner import IScanner
from pip_services3_expressions.io.StringScanner import StringScanner
from .ICommentState import ICommentState
from .INumberState import INumberState
from .IQuoteState import IQuoteState
from .ISymbolState import ISymbolState
from .ITokenizer import ITokenizer
from .IWhitespaceState import IWhitespaceState
from .IWordState import IWordState
from .Token import Token
from .TokenType import TokenType
from .utilities.CharReferenceMap import CharReferenceMap
from .utilities.CharValidator import CharValidator


class AbstractTokenizer(ITokenizer, ABC):
    """
    Implements an abstract tokenizer class.
    """

    def __init__(self):
        self.__map = CharReferenceMap()
        self.skip_unknown: bool = None
        self.skip_whitespaces: bool = None
        self.skip_comments: bool = None
        self.skip_eof: bool = None
        self.merge_whitespaces: bool = None
        self.unify_numbers: bool = None
        self.decode_strings: bool = None
        self.comment_state: ICommentState = None
        self.number_state: INumberState = None
        self.quote_state: IQuoteState = None
        self.symbol_state: ISymbolState = None
        self.whitespace_state: IWhitespaceState = None
        self.word_state: IWordState = None

        self._scanner: IScanner = None
        self._next_token: Token = None
        self._last_token_type = TokenType.Unknown

    def get_character_state(self, symbol):
        return self.__map.lookup(symbol)

    def set_character_state(self, from_symbol, to_symbol, state):
        self.__map.add_interval(from_symbol, to_symbol, state)

    def clear_character_states(self):
        self.__map.clear()

    @property
    def scanner(self) -> IScanner:
        return self._scanner

    @scanner.setter
    def scanner(self, value: IScanner):
        self._scanner = value
        self._next_token = None
        self._last_token_type = TokenType.Unknown

    def has_next_token(self):
        self._next_token = self._read_next_token() if self._next_token is None else self._next_token
        return self._next_token is not None

    def next_token(self) -> Token:
        token = self._read_next_token() if self._next_token is None else self._next_token
        self._next_token = None
        return token

    def _read_next_token(self):
        if self._scanner is None:
            return None

        token = None

        while True:
            # Read character
            next_char = self._scanner.peek()

            # If reached Eof then exit
            if CharValidator.is_eof(next_char):
                token = None
                break

            # Get state for character
            state = self.get_character_state(next_char)
            if state is not None:
                token = state.next_token(self._scanner, self)

            # Check for unknown characters and endless loops...
            if token is None or token.value == '':
                token = Token(TokenType.Unknown, chr(self._scanner.read()))

            # Skip unknown characters if option set.
            if token.type == TokenType.Unknown and self.skip_unknown:
                self._last_token_type = token.type
                continue

            # Decode strings is option set.
            if state is not None and hasattr(state, 'decode_string') and self.decode_strings:
                token = Token(token.type, self.quote_state.decode_string(token.value, next_char))

            # Skips comments if option set.
            if token.type == TokenType.Comment and self.skip_comments:
                self._last_token_type = token.type
                continue

            # Skips whitespaces if option set.
            if token.type == TokenType.Whitespace and \
                    self._last_token_type == TokenType.Whitespace and \
                    self.skip_whitespaces:
                self._last_token_type = token.type
                continue

            # Unifies whitespaces if option set.
            if token.type == TokenType.Whitespace and self.merge_whitespaces:
                token = Token(TokenType.Whitespace, " ")

            # Unifies numbers if option set.
            if self.unify_numbers and \
                    (token.type == TokenType.Integer or
                     token.type == TokenType.Float or
                     token.type == TokenType.HexDecimal):
                token = Token(TokenType.Number, token.value)

            break

        # Adds an Eof if option is not set.
        if token is None and self._last_token_type != TokenType.Eof and not self.skip_eof:
            token = Token(TokenType.Eof, None)

        # Assigns the last token type
        self._last_token_type = token.type if token is not None else TokenType.Eof

        return token

    def tokenize_stream(self, scanner: IScanner):
        self.scanner = scanner
        tokenize_list = []
        token = self.next_token()

        while token is not None:
            tokenize_list.append(token)
            token = self.next_token()

        return tokenize_list

    def tokenize_buffer(self, buffer):
        scanner = StringScanner(buffer)
        return self.tokenize_stream(scanner)

    def tokenize_stream_to_string(self, scanner: IScanner):
        self.scanner = scanner
        string_list = []
        token = self.next_token()

        while token is not None:
            string_list.append(token.value)
            token = self.next_token()

        return string_list

    def tokenize_buffer_to_strings(self, buffer):
        scanner = StringScanner(buffer)
        return self.tokenize_stream_to_string(scanner)
