docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) --tag reranker -f docker/reranker/Dockerfile .

if [ -z ${CUDA_VISIBLE_DEVICES} ]; then
  export CUDA_VISIBLE_DEVICES=all
fi

docker run --user "$(id -u):$(id -g)" -e PYTHONUNBUFFERED=1 --runtime=nvidia -e NVIDIA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES --rm -v $(pwd)/data:/reranker/data --name reranker reranker python rerank.py --device cuda
