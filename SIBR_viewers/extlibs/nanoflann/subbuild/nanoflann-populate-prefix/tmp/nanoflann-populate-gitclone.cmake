
if(NOT "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitinfo.txt" IS_NEWER_THAN "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitclone-lastrun.txt")
  message(STATUS "Avoiding repeated git clone, stamp file is up to date: '/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitclone-lastrun.txt'")
  return()
endif()

execute_process(
  COMMAND ${CMAKE_COMMAND} -E rm -rf "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/nanoflann"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to remove directory: '/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/nanoflann'")
endif()

# try the clone 3 times in case there is an odd git clone issue
set(error_code 1)
set(number_of_tries 0)
while(error_code AND number_of_tries LESS 3)
  execute_process(
    COMMAND "/usr/bin/git"  clone --no-checkout --config "advice.detachedHead=false" "https://gitlab.inria.fr/sibr/libs/nanoflann.git" "nanoflann"
    WORKING_DIRECTORY "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann"
    RESULT_VARIABLE error_code
    )
  math(EXPR number_of_tries "${number_of_tries} + 1")
endwhile()
if(number_of_tries GREATER 1)
  message(STATUS "Had to git clone more than once:
          ${number_of_tries} times.")
endif()
if(error_code)
  message(FATAL_ERROR "Failed to clone repository: 'https://gitlab.inria.fr/sibr/libs/nanoflann.git'")
endif()

execute_process(
  COMMAND "/usr/bin/git"  checkout 7a20a9ac0a1d34850fc3a9e398fc4a7618e8a69a --
  WORKING_DIRECTORY "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/nanoflann"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to checkout tag: '7a20a9ac0a1d34850fc3a9e398fc4a7618e8a69a'")
endif()

set(init_submodules TRUE)
if(init_submodules)
  execute_process(
    COMMAND "/usr/bin/git"  submodule update --recursive --init 
    WORKING_DIRECTORY "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/nanoflann"
    RESULT_VARIABLE error_code
    )
endif()
if(error_code)
  message(FATAL_ERROR "Failed to update submodules in: '/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/nanoflann'")
endif()

# Complete success, update the script-last-run stamp file:
#
execute_process(
  COMMAND ${CMAKE_COMMAND} -E copy
    "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitinfo.txt"
    "/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitclone-lastrun.txt"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to copy script-last-run stamp file: '/root/autodl-tmp/gaussian-splatting/SIBR_viewers/extlibs/nanoflann/subbuild/nanoflann-populate-prefix/src/nanoflann-populate-stamp/nanoflann-populate-gitclone-lastrun.txt'")
endif()

