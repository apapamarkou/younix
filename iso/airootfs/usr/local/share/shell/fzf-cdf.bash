cdf() {
    local DIR
    
    # Use find to list directories, excluding paths that contain /.cache or /.mozilla
    DIR=$(find . -type d \
        ! -path '*/.cache*' \
        ! -path '*/.mozilla*' 2>/dev/null | fzf \
        --prompt=" cd > " \
        --preview 'tree -L 1 {} | head -20' \
        --preview-window=right:50%:wrap \
        --height=80%)
        
    # Change directory if a choice was made
    [ -n "$DIR" ] && cd "$DIR"
}
