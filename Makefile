.PHONY: clean package

package: data.zip

data.zip: data-r.csv data-g.csv data-b.csv
	zip -9 data.zip data-r.csv data-g.csv data-b.csv

clean:
	rm data-r.csv data-g.csv data-b.csv
	rm data.zip
