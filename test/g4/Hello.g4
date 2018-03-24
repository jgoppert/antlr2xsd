grammar Modelica;

//=========================================================
//  B.2.1 Stored Definition - Within
//=========================================================

// B.2.1.1 ------------------------------------------------
stored_definition :
    (stored_definition_class)*
    ;

stored_definition_class :
    FINAL? ';' # final
    | EACH? ';' # each
    ;
