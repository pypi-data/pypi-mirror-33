set(OUTPUT_PREFIX Library)

add_custom_target(
  library-common
  COMMAND ${CMAKE_COMMAND} -E copy_directory
  "${CMAKE_CURRENT_SOURCE_DIR}"
  "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/${OUTPUT_PREFIX}/Common"
)

if(APPLE)
  install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DESTINATION "${MACOSX_BUNDLE_NAME}.app/Contents/Resources/${OUTPUT_PREFIX}"
    COMPONENT standard-library-common
  )
elseif(UNIX)
  install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DESTINATION "usr/share/sympathy/${OUTPUT_PREFIX}"
    COMPONENT standard-library-common
  )
else()
  install(
    DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DESTINATION ${OUTPUT_PREFIX}
    COMPONENT standard-library-common
  )
endif()
