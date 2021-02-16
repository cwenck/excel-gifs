.PHONY: clean package

package: data.zip

data.zip: *.csv
	zip -9 data.zip *.csv

clean:
	rm *.csv
	rm data.zip
