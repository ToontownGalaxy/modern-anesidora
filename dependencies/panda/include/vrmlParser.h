/* A Bison parser, made by GNU Bison 2.7.  */

/* Bison interface for Yacc-like parsers in C
   
      Copyright (C) 1984, 1989-1990, 2000-2012 Free Software Foundation, Inc.
   
   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.
   
   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

#ifndef YY_VRMLYY_BUILT_X64_TMP_VRMLPARSER_YXX_H_INCLUDED
# define YY_VRMLYY_BUILT_X64_TMP_VRMLPARSER_YXX_H_INCLUDED
/* Enabling traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int vrmlyydebug;
#endif

/* Tokens.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
   /* Put the tokens into the symbol table, so that GDB and other debuggers
      know about them.  */
   enum yytokentype {
     IDENTIFIER = 258,
     DEF = 259,
     USE = 260,
     PROTO = 261,
     EXTERNPROTO = 262,
     TO = 263,
     IS = 264,
     ROUTE = 265,
     SFN_NULL = 266,
     EVENTIN = 267,
     EVENTOUT = 268,
     FIELD = 269,
     EXPOSEDFIELD = 270,
     SFBOOL = 271,
     SFCOLOR = 272,
     SFFLOAT = 273,
     SFIMAGE = 274,
     SFINT32 = 275,
     SFNODE = 276,
     SFROTATION = 277,
     SFSTRING = 278,
     SFTIME = 279,
     SFVEC2F = 280,
     SFVEC3F = 281,
     MFCOLOR = 282,
     MFFLOAT = 283,
     MFINT32 = 284,
     MFROTATION = 285,
     MFSTRING = 286,
     MFVEC2F = 287,
     MFVEC3F = 288,
     MFNODE = 289
   };
#endif
/* Tokens.  */
#define IDENTIFIER 258
#define DEF 259
#define USE 260
#define PROTO 261
#define EXTERNPROTO 262
#define TO 263
#define IS 264
#define ROUTE 265
#define SFN_NULL 266
#define EVENTIN 267
#define EVENTOUT 268
#define FIELD 269
#define EXPOSEDFIELD 270
#define SFBOOL 271
#define SFCOLOR 272
#define SFFLOAT 273
#define SFIMAGE 274
#define SFINT32 275
#define SFNODE 276
#define SFROTATION 277
#define SFSTRING 278
#define SFTIME 279
#define SFVEC2F 280
#define SFVEC3F 281
#define MFCOLOR 282
#define MFFLOAT 283
#define MFINT32 284
#define MFROTATION 285
#define MFSTRING 286
#define MFVEC2F 287
#define MFVEC3F 288
#define MFNODE 289



#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef union YYSTYPE
{
/* Line 2058 of yacc.c  */
#line 115 "pandatool/src/vrml/vrmlParser.yxx"

  char *string;
  VrmlFieldValue fv;
  VrmlNode *node;
  MFArray *mfarray;
  SFNodeRef nodeRef;
  VrmlScene *scene;


/* Line 2058 of yacc.c  */
#line 135 "built_x64/tmp/vrmlParser.yxx.h"
} YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define yystype YYSTYPE /* obsolescent; will be withdrawn */
# define YYSTYPE_IS_DECLARED 1
#endif

extern YYSTYPE vrmlyylval;

#ifdef YYPARSE_PARAM
#if defined __STDC__ || defined __cplusplus
int vrmlyyparse (void *YYPARSE_PARAM);
#else
int vrmlyyparse ();
#endif
#else /* ! YYPARSE_PARAM */
#if defined __STDC__ || defined __cplusplus
int vrmlyyparse (void);
#else
int vrmlyyparse ();
#endif
#endif /* ! YYPARSE_PARAM */

#endif /* !YY_VRMLYY_BUILT_X64_TMP_VRMLPARSER_YXX_H_INCLUDED  */
