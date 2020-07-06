package main

import (
	"fmt"
	"os"

	"github.com/nuagenetworks/go-bambou/bambou"
	"github.com/nuagenetworks/vspk-go/vspk"
)

var vsdURL = "https://vsd01.philippe.plm.nuagedemo.net:8443"
var vsdUser = "csproot"
var vsdPass = "csproot"
var vsdEnterprise = "csp"

func handleError(err *bambou.Error, t string, o string) {
	if err != nil {
		fmt.Println("Unable to " + o + " \"" + t + "\": " + err.Description)
		os.Exit(1)
	}
}

func main() {
	s, root := vspk.NewSession(vsdUser, vsdPass, vsdEnterprise, vsdURL)
	if err := s.Start(); err != nil {
		fmt.Println("Unable to connect to Nuage VSD: " + err.Description)
		os.Exit(1)
	}

	entAName := "Go 1"
	entA := &vspk.Enterprise{Name: entAName}
	entBName := "Go 2"
	entB := &vspk.Enterprise{Name: entBName}

	err := root.CreateEnterprise(entA)
	handleError(err, "Enterprise", "CREATE")
	err = root.CreateEnterprise(entB)
	handleError(err, "Enterprise", "CREATE")

	fmt.Printf("Enterprise A ID: %s - Customer ID: %d\n",  entA.ID, entA.CustomerID)
	fmt.Printf("Enterprise B ID: %s - Customer ID: %d\n",  entB.ID, entB.CustomerID)

	entC:= &vspk.Enterprise{ID: entB.ID}
	err = entC.Fetch()
	handleError(err, "Enterprise", "FETCH")
	fmt.Printf("Enterprise C ID: %s - Customer ID: %d\n",  entC.ID, entC.CustomerID)

	entA.Delete()
	entB.Delete()
}
