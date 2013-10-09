nfail=0

pushd projections > /dev/null
echo "Running tests on different projections and argument combinations."
./runtest.sh
((nfail += $?))
if [ $nfail -eq 0 ] ; then
    echo "SUCCESS"
else
    echo "$nfail tests failed."
fi
popd > /dev/null

exit $nfail
