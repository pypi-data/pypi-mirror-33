#------------------------------------------------------------------------------#
# only define if less than 3.10.0
#

get_property(_PROP GLOBAL
    PROPERTY __CHECKINCLUDEGUARD_VAR__ SET)
if(_PROP)
    return()
endif()
set_property(GLOBAL PROPERTY __CHECKINCLUDEGUARD_VAR__ TRUE)


if(CMAKE_VERSION VERSION_LESS "3.10.0")
macro(include_guard)

    if("${ARGN}" STREQUAL "GLOBAL")
        set(_GLOBAL ON)
    elseif("${ARGN}" STREQUAL "DIRECTORY")
        set(_DIRECTORY ON)
    else()
        set(_VARIABLE ON)
    endif()

    set(_VARNAME __${CMAKE_CURRENT_LIST_FILE}_VAR__)

    if(_GLOBAL)
        get_property(_PROP
            GLOBAL
            PROPERTY ${_VARNAME}
            SET
        )
        if(_PROP)
            return()
        endif()
        set_property(GLOBAL PROPERTY ${_VARNAME} TRUE)

    elseif(_DIRECTORY)
        get_property(_PROP
            DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
            PROPERTY ${_VARNAME}
            SET
        )

        if(_PROP)
            return()
        endif()

        set_property(DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
            PROPERTY ${_VARNAME} TRUE)

    elseif(_VARIABLE)
        get_property(_PROP
            VARIABLE
            PROPERTY ${_VARNAME}
            SET
        )

        if(_PROP)
            return()
        endif()

        set_property(PROPERTY ${_VARNAME} TRUE)
    endif()

endmacro(include_guard)
endif(CMAKE_VERSION VERSION_LESS "3.10.0")

#------------------------------------------------------------------------------#
