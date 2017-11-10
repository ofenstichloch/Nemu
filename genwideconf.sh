num=$1
echo "nodes:" > config/wide$num
echo "  switch0:" >> config/wide$num
echo "    type: switch" >> config/wide$num
for i in `seq 1 $num` 
do
	echo "  node$i:" >> config/wide$num
	echo "    type: client" >> config/wide$num
	echo "  router$i:" >> config/wide$num
	echo "    type: router" >> config/wide$num
	echo "  switch$i:" >> config/wide$num
	echo "    type: switch" >> config/wide$num
done
echo "edges:" >> config/wide$num
for i in `seq 1 $num`
do
	echo "- [switch$i, node$i]" >> config/wide$num
	echo "- [router$i, switch$i]" >> config/wide$num
	echo "- [router$i, switch0]" >> config/wide$num
done
