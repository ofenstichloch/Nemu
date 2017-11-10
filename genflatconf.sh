num=$1
echo "nodes:" > config/flat$num
for i in `seq 1 $num` 
do
	echo "  node$i:" >> config/flat$num
	echo "    type: client" >> config/flat$num
done
echo "  router1:" >> config/flat$num
echo "    type: router" >> config/flat$num
echo "  switch1:" >> config/flat$num
echo "    type: switch" >> config/flat$num
echo "edges:" >> config/flat$num
for i in `seq 1 $num`
do
	echo "- [switch1, node$i]" >> config/flat$num
done
echo "- [router1, switch1]" >> config/flat$num
