grammar FlexTag;

document
    : (NL | COMMENT | MULTILINE_COMMENT)* tagElements ((NL | COMMENT | MULTILINE_COMMENT)+ tagElements)* (NL | COMMENT | MULTILINE_COMMENT)* EOF
    ;

tagElements
    : tagElement
    ;

tagElement
    : fullTag
    | selfClosingTag
    | jsonTag
    ;

fullTag
    : (OPEN_TAG | SIMPLE_TAG)
      content 
      CLOSE_TAG
    ;

jsonTag
    : JSON_OPEN_TAG
      content
      CLOSE_TAG
    ;

selfClosingTag
    : SELF_CLOSE_TAG
    | DATA_SELF_CLOSE_TAG
    | DATA_TAG_ONLY_TAG
    | DATA_PATH_ONLY_TAG
    | DATA_SIMPLE_SELF_CLOSE_TAG
    | JSON_SELF_CLOSE_TAG
    ;

content
    : contentLine+
    ;

contentLine
    : TEXT NL
    ;

// JSON specific tags
JSON_OPEN_TAG : '[[DATA' WS_OR_NL* '{' .*? '}]]' NL ;
JSON_SELF_CLOSE_TAG : '[[DATA' WS_OR_NL* '{' .*? '}/]]' ;

// Original tag rules
OPEN_TAG : '[[DATA' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* ':' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* [a-zA-Z0-9]+ 
          ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR (TAG|PATH))* 
          ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR NESTED_JSON)? 
          ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* ']]' NL ;

SIMPLE_TAG : '[[DATA]]' NL ;
CLOSE_TAG : '[[' [ \t]* '/DATA' [ \t]* ']]' ;
SELF_CLOSE_TAG : '[[' [ \t]* '/DATA/' [ \t]* ']]' ;

DATA_SELF_CLOSE_TAG : '[[DATA' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* ':' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* [a-zA-Z0-9]+ 
                     ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR (TAG|PATH))* 
                     ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR NESTED_JSON)? 
                     ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* '/' [ \t]* ']]' ;

DATA_TAG_ONLY_TAG : '[[DATA' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* TAG (META_SEPARATOR (TAG|PATH))* 
                    ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR NESTED_JSON)? 
                    ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* '/' [ \t]* ']]' ;

DATA_PATH_ONLY_TAG : '[[DATA' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* PATH (META_SEPARATOR (TAG|PATH))* 
                     ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* (META_SEPARATOR NESTED_JSON)? 
                     ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* '/' [ \t]* ']]' ;

DATA_SIMPLE_SELF_CLOSE_TAG : '[[' [ \t]* 'DATA' [ \t]* '/' [ \t]* ']]' ;

// Comment rules
COMMENT : '//' ~[\r\n]* NL -> channel(HIDDEN) ;
MULTILINE_COMMENT : '/*' .*? '*/' NL? -> channel(HIDDEN) ;

fragment WS_OR_NL : [ \t] | '\r'? '\n' [ \t]* ;
fragment ID : [a-zA-Z0-9]+ ;
fragment TAG : '#' [a-zA-Z][a-zA-Z0-9_]* ;
fragment PATH : '.' [a-zA-Z][a-zA-Z0-9_]* ('.' [a-zA-Z][a-zA-Z0-9_]*)* ;
fragment META_SEPARATOR : ',' ([ \t]* '\r'? '\n' [ \t]* | [ \t]+)* ;

fragment NESTED_JSON : '{' JSON_CONTENT* '}' ;
fragment JSON_CONTENT : ~[{}] | NESTED_JSON ;

TEXT : ~('[' | '\r' | '\n')+ ;
NL : ('\r\n' | '\n' | '\r') ;
WS : [ \t]+ -> skip ;