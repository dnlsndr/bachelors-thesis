package main

import (
	"fmt"
	"time"
)

const (
	AllocSize = 100 * 1024 * 50        // 100 MB
	Threshold = 4 * 1024 * 1024 * 1024 // 4 GB
)

func main() {
	var allocations [][]byte
	var allocated int64 = 0

	for {
		if allocated >= Threshold {
			allocations = nil
			allocated = 0
			fmt.Println("Memory cleared")
		}

		memory := make([]byte, AllocSize)
		allocations = append(allocations, memory)
		allocated += AllocSize

		fmt.Printf("Allocated: %d MB\n", allocated/1024/1024)
		time.Sleep(1 * time.Second)
	}
}
