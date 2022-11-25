package tuple

import (
	"context"
)

type LazyTuple interface {
	Key() Key
	Data() Data
}

func FilterIterator(it LazyTuple, f *Filter, next func() bool) bool {
	if f.IsAny() {
		return next()
	}
	for next() {
		if f.KeyFilter != nil && !f.KeyFilter.FilterKey(it.Key()) {
			continue
		}
		if f.DataFilter != nil && !f.DataFilter.FilterData(it.Data()) {
			continue
		}
		return true
	}
	return false
}

type Deleter interface {
	// DeleteTuplesByKey removes tuples by key.
	DeleteTuplesByKey(ctx context.Context, keys []Key) error
	Scanner
}

func DeleteEach(ctx context.Context, d Deleter, f *Filter) error {
	// TODO: recognize fixed filters
	it := d.Scan(&ScanOptions{
		KeysOnly: true,
		Filter:   f,
	})
	defer it.Close()

	const batch = 100
	var buf []Key
	flush := func() error {
		if len(buf) == 0 {
			return nil
		}
		err := d.DeleteTuplesByKey(ctx, buf)
		if err != nil {
			return err
		}
		buf = buf[:0]
		return nil
	}
	for it.Next(ctx) {
		buf = append(buf, it.Key())
		if len(buf) >= batch {
			if err := flush(); err != nil {
				return err
			}
		}
	}
	if err := flush(); err != nil {
		return err
	}
	return it.Err()
}
