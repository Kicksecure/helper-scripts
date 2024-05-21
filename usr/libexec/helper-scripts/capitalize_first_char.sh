## Capitalize only the first char of a string.
capitalize_first_char(){
  echo "${1:-}" | awk '{$1=toupper(substr($1,0,1))substr($1,2)}1'
}

