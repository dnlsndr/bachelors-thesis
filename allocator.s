	.file	"allocator.c"
	.text
	.globl	AllocSize
	.section	.rodata
	.align 8
	.type	AllocSize, @object
	.size	AllocSize, 8
AllocSize:
	.quad	1048576
	.globl	Threshold
	.align 8
	.type	Threshold, @object
	.size	Threshold, 8
Threshold:
	.quad	20971520
.LC0:
	.string	"Memory cleared"
.LC1:
	.string	"Allocated: %lu MB\n"
	.text
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$48, %rsp
	movq	$0, -48(%rbp)
	movq	$0, -40(%rbp)
	movq	$10, -32(%rbp)
	movq	-32(%rbp), %rax
	salq	$3, %rax
	movq	%rax, %rdi
	call	malloc@PLT
	movq	%rax, -24(%rbp)
.L6:
	movl	$1048576, %edx
	movq	-48(%rbp), %rax
	addq	%rdx, %rax
	movl	$20971520, %edx
	cmpq	%rax, %rdx
	jnb	.L2
	movq	$0, -16(%rbp)
	jmp	.L3
.L4:
	movq	-16(%rbp), %rax
	leaq	0(,%rax,8), %rdx
	movq	-24(%rbp), %rax
	addq	%rdx, %rax
	movq	(%rax), %rax
	movq	%rax, %rdi
	call	free@PLT
	addq	$1, -16(%rbp)
.L3:
	movq	-16(%rbp), %rax
	cmpq	-40(%rbp), %rax
	jb	.L4
	movq	$0, -48(%rbp)
	movq	$0, -40(%rbp)
	leaq	.LC0(%rip), %rax
	movq	%rax, %rdi
	call	puts@PLT
.L2:
	movq	-40(%rbp), %rax
	cmpq	-32(%rbp), %rax
	jb	.L5
	salq	-32(%rbp)
	movq	-32(%rbp), %rax
	leaq	0(,%rax,8), %rdx
	movq	-24(%rbp), %rax
	movq	%rdx, %rsi
	movq	%rax, %rdi
	call	realloc@PLT
	movq	%rax, -24(%rbp)
.L5:
	movl	$1048576, %eax
	movq	%rax, %rdi
	call	malloc@PLT
	movq	%rax, -8(%rbp)
	movq	-40(%rbp), %rax
	leaq	1(%rax), %rdx
	movq	%rdx, -40(%rbp)
	leaq	0(,%rax,8), %rdx
	movq	-24(%rbp), %rax
	addq	%rax, %rdx
	movq	-8(%rbp), %rax
	movq	%rax, (%rdx)
	movl	$1048576, %eax
	addq	%rax, -48(%rbp)
	movq	-48(%rbp), %rax
	shrq	$20, %rax
	movq	%rax, %rsi
	leaq	.LC1(%rip), %rax
	movq	%rax, %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	$1, %edi
	call	sleep@PLT
	jmp	.L6
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"GCC: (GNU) 13.2.1 20230801"
	.section	.note.GNU-stack,"",@progbits
