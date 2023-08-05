
```
parameters:
 - IV: input values: iterator over a list of input values
 - max_pattern: maximum number of different patterns

init:
    PF(max_patterns)

alogorithm
    for iv in IV:
        PF.add_value( iv )

PF.add_value( iv ):
    if self.free_slots:
            PF.add( EmptyPattern( iv ) )
        else:

```

