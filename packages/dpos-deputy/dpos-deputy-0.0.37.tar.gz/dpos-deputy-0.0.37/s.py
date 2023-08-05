
for i in ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eight", "Ninth", "Tenth",]:
    print(
        """
        comp.{i}.Ticker = p.{i}.Ticker
	    comp.{i}.Verbose = p.{i}.VerboseName
	    comp.{i}.DefaultSupply = p.{i}.DefaultSupply
        """.format(i=i)
    )