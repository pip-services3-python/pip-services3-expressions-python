# -*- coding: utf-8 -*-

from pip_services3_expressions.io.StringPushbackReader import StringPushbackReader
from pip_services3_expressions.tokenizers.TokenType import TokenType
from pip_services3_expressions.tokenizers.generic.SymbolRootNode import SymbolRootNode


class TestSymbolRootNode:

    def test_next_token(self):
        node = SymbolRootNode()
        node.add("<", TokenType.Symbol)
        node.add("<<", TokenType.Symbol)
        node.add("<>", TokenType.Symbol)

        reader = StringPushbackReader("<A<<<>")

        token = node.next_token(reader)
        assert "<" == token.value

        token = node.next_token(reader)
        assert "A" == token.value

        token = node.next_token(reader)
        assert "<<" == token.value

        token = node.next_token(reader)
        assert "<>" == token.value

    def test_single_token(self):
        node = SymbolRootNode()

        reader = StringPushbackReader("<A")

        token = node.next_token(reader)
        assert "<" == token.value
        assert TokenType.Symbol == token.type
