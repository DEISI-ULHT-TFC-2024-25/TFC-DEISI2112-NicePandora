#include <getopt.h>
#include <clang-c/Index.h>
#include <stdio.h>
#include <string.h>

static int globalVariableDetected = 0;

// Helper function to check if a variable declaration has the const specifier
static int hasConstSpecifier(CXCursor cursor) {
    CXTranslationUnit translationUnit = clang_Cursor_getTranslationUnit(cursor);
    CXSourceRange range = clang_getCursorExtent(cursor);
    CXToken* tokens;
    unsigned int numTokens;
    clang_tokenize(translationUnit, range, &tokens, &numTokens);
    
    int hasConst = 0;
    for (unsigned int i = 0; i < numTokens; i++) {
        CXString tokenSpelling = clang_getTokenSpelling(translationUnit, tokens[i]);
        const char* tokenStr = clang_getCString(tokenSpelling);
        if (strcmp(tokenStr, "const") == 0) {
            hasConst = 1;
            break;
        }
        clang_disposeString(tokenSpelling);
    }
    
    clang_disposeTokens(translationUnit, tokens, numTokens);
    return hasConst;
}

// Callback function to visit each cursor in the AST
static CXChildVisitResult findGlobalVariables(CXCursor cursor, CXCursor parent, CXClientData client_data) {
    if (clang_getCursorKind(cursor) == CXCursor_VarDecl) {
        if (hasConstSpecifier(cursor))
            return CXChildVisit_Continue; // if it's const, ignore

        // Check if the variable is a function parameter
        CXCursor parentCursor = clang_getCursorSemanticParent(cursor);
        if (clang_getCursorKind(parentCursor) == CXCursor_FunctionDecl) {
            return CXChildVisit_Continue;
        }

        // Get the location of the variable
        CXSourceLocation location = clang_getCursorLocation(cursor);
        CXFile file;
        unsigned int line, column, offset;
        clang_getFileLocation(location, &file, &line, &column, &offset);
        const char* filename = clang_getCString(clang_getFileName(file));

        // Ignore variables defined in ignored paths
        const char* ignorePaths = (const char*)client_data;
        const char* token = strtok((char*)ignorePaths, ":");
        while (token != NULL) {
            if (strstr(filename, token) != NULL) {
                return CXChildVisit_Continue;
            }
            token = strtok(NULL, ":");
        }

        // Print the global variable and its location
        printf("Variable: %s\n", clang_getCString(clang_getCursorSpelling(cursor)));
        printf("  Location: %s:%u:%u\n", filename, line, column);

        globalVariableDetected = 1;
    }

    return CXChildVisit_Recurse;
}

int main(int argc, char* argv[]) {
    int opt;
    
    // Option flags
    int ignorePathsFlag = 0;
    const char* ignorePaths = NULL;
    
    // Process command-line options
    while ((opt = getopt(argc, argv, "i:")) != -1) {
        switch (opt) {
            case 'i':
                ignorePathsFlag = 1;
                ignorePaths = optarg;
                break;
            default:
                fprintf(stderr, "Usage: %s [-i ignore_path1:ignore_path2:...] file1.c file2.c ...\n", argv[0]);
                return 1;
        }
    }
    
    // Check if any input files are provided
    if (optind >= argc) {
        fprintf(stderr, "Please provide one or more input file names.\n");
        return 1;
    }
    
    // Iterate over the remaining command-line arguments (input file names)
    for (int i = optind; i < argc; i++) {
        const char* filename = argv[i];
        printf("Checking file: %s\n", filename);
        
        // Create libclang index
        CXIndex index = clang_createIndex(0, 0);
        
        // Parse the translation unit from the source file
        CXTranslationUnit translationUnit = clang_parseTranslationUnit(
            index, filename, NULL, 0, NULL, 0, CXTranslationUnit_None);
        
        if (translationUnit == NULL) {
            printf("Error parsing translation unit.\n");
            return 1;
        }
        
        // Get the cursor for the translation unit
        CXCursor cursor = clang_getTranslationUnitCursor(translationUnit);
        
        // Visit the children cursors in the AST and find global variables
        clang_visitChildren(cursor, findGlobalVariables, (CXClientData)ignorePaths);
        
        // Dispose the translation unit and the index
        clang_disposeTranslationUnit(translationUnit);
        clang_disposeIndex(index);
    }
    
    // Check if any global variable was detected
    if (globalVariableDetected) {
        return 1;
    }
    
    return 0;
}

