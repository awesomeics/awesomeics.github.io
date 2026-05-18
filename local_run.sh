docker run \
  -v $(pwd):/srv/jekyll \
  -v $(pwd)/_site:/srv/jekyll/_site \
  jekyll/builder:latest \
  /bin/bash -c "chmod -R 777 /srv/jekyll && jekyll build --future --trace"

docker run \
  -p 4000:4000 \
  -v $(pwd):/srv/jekyll \
  jekyll/builder:latest \
  /bin/bash -c "gem install webrick && jekyll serve --watch --future --host 0.0.0.0"
