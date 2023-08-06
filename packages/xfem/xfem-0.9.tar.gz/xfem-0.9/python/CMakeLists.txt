if(NETGEN_USE_PYTHON)
    add_ngsolve_python_module(ngsxfem_py python_ngsxfem.cpp)
    set_target_properties(ngsxfem_py PROPERTIES INSTALL_RPATH "${NETGEN_RPATH_TOKEN}/../${NETGEN_PYTHON_RPATH}")

    if(SETUP_PY)
      install(TARGETS ngsxfem_py DESTINATION ${CMAKE_INSTALL_PREFIX}/python)
    else(SETUP_PY)
      install(TARGETS ngsxfem_py DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem)
    endif(SETUP_PY)

    target_link_libraries(ngsxfem_py ngsxfem_lsetcurving ngsxfem_utils ngsxfem_cutint ngsxfem_xfem ngsxfem_spacetime)

    if(NOT SETUP_PY)
    install (FILES
        __init__.py 
        DESTINATION ${NGSOLVE_INSTALL_DIR_PYTHON}/xfem
        COMPONENT xfem
        )
    endif(NOT SETUP_PY)
endif(NETGEN_USE_PYTHON)
