import time
from opustools_pkg import OpusRead

@profile
def printExhaustive(arguments):
	start = time.time()
	eprinter = OpusRead(arguments)
	eprinter.printPairs()
	end = time.time()
	print("%.4f" % float(end-start), "s")

@profile
def printFast(arguments):
	start = time.time()
	eprinter = OpusRead(arguments)
	eprinter.printPairs()
	end = time.time()
	print("%.4f" % float(end-start), "s")

'''
print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, all alignments ")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result" , "-f"])
print("")

'''
print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, all alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result" , "-f"])
print("")
'''
print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, 10 alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result", "-m", "10"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-m", "10"])
print("")

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, 10 alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result", "-m", "10"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-m", "10"])
print("")


print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, all alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-p", "raw"])
print("")

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, all alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-p", "raw"])
print("")

print("Corpus: Books, 3654 alignment pairs, source: en, target: fi, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result", "-m", "10", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-m", "10", "-p", "raw"])
print("")

print("Corpus: Books, 129305 alignment pairs, source: en, target: fr, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result", "-m", "10", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Books", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-m", "10", "-p", "raw"])
print("")


print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, all alignments ")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result" , "-f"])
print("")

print("Corpus: Europarl, 2054543 alignment pairs, source: en, target: fr, all alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result" , "-f"])
print("")

print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, 10 alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result", "-m", "10"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-m", "10"])
print("")

print("Corpus: Europarl, 2054543 alignment pairs, source: en, target: fr, 10 alignments")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result", "-m", "10"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-m", "10"])
print("")

print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, all alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-p", "raw"])
print("")

print("Corpus: Europarl, 2054543 alignment pairs, source: en, target: fr, all alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-p", "raw"])
print("")

print("Corpus: Europarl, 1974717 alignment pairs, source: en, target: fi, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result", "-m", "10", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fi", "-w", "test_result" , "-f", "-m", "10", "-p", "raw"])
print("")

print("Corpus: Europarl, 2054543 alignment pairs, source: en, target: fr, 10 alignments, preprocessing raw")
print("Exhaustive parser:")
printExhaustive(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result", "-m", "10", "-p", "raw"])
print("Fast parser:")
printFast(["-d", "Europarl", "-s", "en", "-t", "fr", "-w", "test_result" , "-f", "-m", "10", "-p", "raw"])
print("")
'''
