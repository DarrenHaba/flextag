# Generated from FlexTag.g4 by ANTLR 4.13.2
from antlr4 import *

if "." in __name__:
    from .FlexTagParser import FlexTagParser
else:
    from FlexTagParser import FlexTagParser


# This class defines a complete listener for a parse tree produced by FlexTagParser.
class FlexTagListener(ParseTreeListener):

    # Enter a parse tree produced by FlexTagParser#document.
    def enterDocument(self, ctx: FlexTagParser.DocumentContext):
        pass

    # Exit a parse tree produced by FlexTagParser#document.
    def exitDocument(self, ctx: FlexTagParser.DocumentContext):
        pass

    # Enter a parse tree produced by FlexTagParser#tagElements.
    def enterTagElements(self, ctx: FlexTagParser.TagElementsContext):
        pass

    # Exit a parse tree produced by FlexTagParser#tagElements.
    def exitTagElements(self, ctx: FlexTagParser.TagElementsContext):
        pass

    # Enter a parse tree produced by FlexTagParser#tagElement.
    def enterTagElement(self, ctx: FlexTagParser.TagElementContext):
        pass

    # Exit a parse tree produced by FlexTagParser#tagElement.
    def exitTagElement(self, ctx: FlexTagParser.TagElementContext):
        pass

    # Enter a parse tree produced by FlexTagParser#fullTag.
    def enterFullTag(self, ctx: FlexTagParser.FullTagContext):
        pass

    # Exit a parse tree produced by FlexTagParser#fullTag.
    def exitFullTag(self, ctx: FlexTagParser.FullTagContext):
        pass

    # Enter a parse tree produced by FlexTagParser#jsonTag.
    def enterJsonTag(self, ctx: FlexTagParser.JsonTagContext):
        pass

    # Exit a parse tree produced by FlexTagParser#jsonTag.
    def exitJsonTag(self, ctx: FlexTagParser.JsonTagContext):
        pass

    # Enter a parse tree produced by FlexTagParser#selfClosingTag.
    def enterSelfClosingTag(self, ctx: FlexTagParser.SelfClosingTagContext):
        pass

    # Exit a parse tree produced by FlexTagParser#selfClosingTag.
    def exitSelfClosingTag(self, ctx: FlexTagParser.SelfClosingTagContext):
        pass

    # Enter a parse tree produced by FlexTagParser#content.
    def enterContent(self, ctx: FlexTagParser.ContentContext):
        pass

    # Exit a parse tree produced by FlexTagParser#content.
    def exitContent(self, ctx: FlexTagParser.ContentContext):
        pass

    # Enter a parse tree produced by FlexTagParser#contentLine.
    def enterContentLine(self, ctx: FlexTagParser.ContentLineContext):
        pass

    # Exit a parse tree produced by FlexTagParser#contentLine.
    def exitContentLine(self, ctx: FlexTagParser.ContentLineContext):
        pass


del FlexTagParser
