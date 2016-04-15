/* 
 * File:   main.c
 * Author: Ronak
 *
 * Created on January 18, 2016, 10:13 PM
 */

#include <stdio.h>
#include <stdlib.h>
#include <ucontext.h>
#include "mythread.h"
#include "mythreadextra.h"


#define STACK_SIZE 8*1024
int Thread_count = 0;

typedef struct Queue Queue;

typedef struct Thread_st {
    int thread_id;
    ucontext_t context;
    struct Thread_st *parent;
    struct Queue *children;
    int joined;
    int thread_joinall;
}_MyThread;

typedef struct Queue_element {
    struct Thread_st *Thread;
    struct Queue_element *next;
} Queue_element;

struct Queue {
    Queue_element *head;
    Queue_element *tail;
};

typedef struct Semaphore{
    int initial_value;
    int curr_value;
    struct Queue *SemaphoreQ;
}Semaphore;

void Queue_init(Queue *);

int Queue_size(Queue *);

int Queue_element_present(Queue * queue, _MyThread *i);

void addtoQueue(Queue *, _MyThread *);

_MyThread *removefromQueue(Queue *);

_MyThread *delete_element(Queue *, _MyThread *);

ucontext_t CreateExitContext();

_MyThread *running_t, *unix_t;		//holds the current running thread.
Queue *ReadyQ, *blockedQ;

ucontext_t init_context, exit_context;

ucontext_t CreateExitContext(){
    ucontext_t t;
    
    getcontext(&t);
    t.uc_link = 0;
    t.uc_stack.ss_sp = malloc(STACK_SIZE);
    t.uc_stack.ss_size = STACK_SIZE;
    t.uc_stack.ss_flags = 0;
    
    makecontext(&t,MyThreadExit,0);
    return t;   
}

void Queue_init(Queue * queue){
  queue->head = NULL;
  queue->tail = NULL;
}

int Queue_size(Queue * queue){
  int i = 0;
  Queue_element *temp;
  temp = queue->head;
  
  if (queue == NULL){
      printf("Queue is NULL\n");
  }
  
  while(temp!=NULL){
     i++;
     temp=temp->next;
  }
  return(i);
}

int Queue_element_present(Queue * queue, _MyThread *i){
    
    Queue_element *p = malloc(sizeof(Queue_element) );
    
    if( NULL == p )
    {
      printf("Error while allocating memory to Queue element.");
      return -1;
    }
    
    if( queue == NULL || Queue_size(queue) == 0 ){
	return -1;
    }
    
    p = queue->head;
    
    while(1){
        if(p->Thread == i){
            return 1;
        }
        if(p->next == NULL){
            break;
        }
        p = p->next;
    }
    return 0;
}

void addtoQueue(Queue* s, _MyThread *i){
    Queue_element *p = malloc(sizeof(Queue_element) );
      
    if( NULL == p )
    {
      printf("Error while allocating memory to Queue element.");
      return;
    }
 
    p->Thread = i;
    p->next = NULL;
  
    if( NULL == s )
    {
      printf("Queue not initialized\n");
      free(p);
    }
    else if( NULL == s->head && NULL == s->tail )
    {
      s->head = s->tail = p;
    }
    else
    {
      s->tail->next = p;
      s->tail = p;
    }
}

_MyThread *removefromQueue(Queue *s){
    _MyThread *p = malloc(sizeof(_MyThread));
    
    if (s == NULL)
    {
        printf("ERROR: DEQUEUE REQUESTED ON EMPTY QUEUE!\n");
	return NULL;
    }
    
    if(s->head == s->tail){
        p = s->head->Thread;
        s->head = s->tail = NULL;
    }else{
        p = s->head->Thread;
        s->head = s->head->next;
    }
    
    return p;
}

_MyThread *delete_element(Queue * s, _MyThread *thread) 
{
    Queue_element *p = malloc(sizeof(Queue_element));
    p = s->head;
    
    if (s == NULL) /* didn't find it so let's report it and quit */
        {
            printf("Queue is Null, Cannot delete\n");
            return NULL;
        }
    
    // When node to be deleted is head node
    if(p->Thread == thread)
    {
        Queue_element * temp = p;
        if(p->next == NULL)
        {
            s->head = s->tail = NULL;
            return temp->Thread;
        }
        /* Copy the data of next node to head */
        s->head = s->head->next;
        
        return temp->Thread;
    }
    // When not first node, follow the normal deletion process
    
    // find the previous node
    Queue_element * curr = p->next; /* start from the node after the head */
    Queue_element * prev = p;
    
    while(prev->next != NULL && prev->next->Thread != thread)
        prev = prev->next;
 
    // Check if node really exists in Linked List
    if(prev->next == NULL)
    {
        printf("\n Given thread is not present in Queue\n");
        return NULL;
    }

    Queue_element * temp = prev->next;
    // Remove node from Linked List
    prev->next = prev->next->next;
    temp->next = NULL;
    return temp->Thread; 
}


void MyThreadInit(void(*start_funct)(void *), void *args){
    if(Thread_count > 0){
        printf("MyThreadInit can be called only once\n");
        return;        
    }
        
    if(start_funct==NULL){
	printf("start_funct is NULL\n");
	return;
    }
    getcontext(&init_context);
    init_context.uc_link = 0;
    init_context.uc_stack.ss_sp = malloc(STACK_SIZE);
    init_context.uc_stack.ss_size = STACK_SIZE;
    init_context.uc_stack.ss_flags = 0;
    
    exit_context = CreateExitContext();
    
    ReadyQ = (Queue *)malloc(sizeof(Queue));
    blockedQ = (Queue *)malloc(sizeof(Queue));
    Queue_init(ReadyQ);
    Queue_init(blockedQ);
    
    _MyThread *root_t = (_MyThread *)malloc(sizeof(_MyThread));
       
    getcontext(&root_t->context);
    //root_t->context.uc_link = 0;
    root_t->context.uc_link = &exit_context;
    root_t->context.uc_stack.ss_sp = malloc(STACK_SIZE);
    root_t->context.uc_stack.ss_size = STACK_SIZE;
    root_t->context.uc_stack.ss_flags = 0;
    root_t->thread_id = Thread_count;
    root_t->joined = 0;
    root_t->thread_joinall = 0;
    root_t->parent = NULL;
    root_t->children = (Queue *)malloc(sizeof(Queue));
    Queue_init(root_t->children);    
    makecontext(&root_t->context, (void(*) ())start_funct,1,args);

    running_t = (_MyThread *)malloc(sizeof(_MyThread));
    running_t = root_t;  
    
    //printf("Thread id: %d\n",Thread_count); 
    Thread_count++;  
    
    swapcontext(&init_context,&root_t->context);
    //swapcontext(&unix_t->context,&root_t->context);
    
}

MyThread MyThreadCreate(void(*start_funct)(void *), void *args){
    
    if(Thread_count == 0){
        printf("MyThreadCreate called before MyThreadInit.\n");
        return NULL;
    }   
    
    _MyThread *newThread = (_MyThread *)malloc(sizeof(_MyThread));
    
    getcontext(&newThread->context);
   // newThread->context.uc_link = 0;
    newThread->context.uc_link = &exit_context;
    newThread->context.uc_stack.ss_sp = malloc(STACK_SIZE);
    newThread->context.uc_stack.ss_size = STACK_SIZE;
    newThread->context.uc_stack.ss_flags = 0;

    newThread->thread_id = Thread_count;
    newThread->joined = 0;
    newThread->thread_joinall = 0;
    newThread->parent = running_t;
    newThread->children = (Queue *)malloc(sizeof(Queue));
    Queue_init(newThread->children);
    makecontext(&newThread->context, (void(*) ())start_funct,1,args);
        
    addtoQueue(running_t->children, newThread);
    addtoQueue(ReadyQ, newThread);
    Thread_count++;
    
    return(MyThread)newThread;
}

void MyThreadYield(void){
    _MyThread *current = running_t;

    if (ReadyQ == NULL)
    {
	printf("Thread yield..Ready Q not initialized.\n");
	return;
    }
    
    if (Queue_size(ReadyQ) == 0)
    {
	printf("No Thread to yield.\n");
	return;
    }

    addtoQueue(ReadyQ,running_t);
    running_t = removefromQueue(ReadyQ);

    if (running_t == unix_t){
        addtoQueue(ReadyQ,running_t);
        running_t = removefromQueue(ReadyQ);
    }

    getcontext(&current->context);
    swapcontext(&current->context,&running_t->context);

}

int MyThreadJoin(MyThread thread){

    int found = 0;
    _MyThread * t = thread;
    
    if (t->parent != running_t){
        //printf("Join, Thread is not immediate child\n");
        return -1;
    }
    else{
        Queue_element * p = malloc(sizeof(Queue_element));

        //Add logic if the child is already terminated, return -1

        if ((Queue_element_present(running_t->children, t)) != 1){
            //printf("Join, Child executed already\n");
            return 0;
        }

        // Thread is the immediate child. Continue-
        _MyThread *current = running_t;
        t->joined = 1;
        addtoQueue(blockedQ,running_t);
        running_t->thread_joinall += 1;
        running_t = removefromQueue(ReadyQ);

        if (running_t == unix_t && Queue_size != 0){
            addtoQueue(ReadyQ,running_t);
            running_t = removefromQueue(ReadyQ);
            //swapcontext(&current->context,&running_t->context);
        }

        swapcontext(&current->context,&running_t ->context);

        return 0;
    }
}

void MyThreadJoinAll(void){
    _MyThread *toRun = (_MyThread*)malloc(sizeof(_MyThread));
    Queue_element *p = (Queue_element*)malloc(sizeof(Queue_element));
    
    if( running_t->children==NULL || Queue_size(running_t->children)==0 ){
	//printf("MyThreadJoinAll, thread has no active kid.\n");
	return;
    }
    
    running_t->thread_joinall = Queue_size(running_t->children);
    
    p = running_t->children->head;
    while(p->next != NULL){
        p->Thread->joined = 1;
        p = p->next;
    }
    p->Thread->joined = 1;
    
    _MyThread *current = running_t;
    addtoQueue(blockedQ,running_t);
    toRun = removefromQueue(ReadyQ);
    
    running_t = toRun;
    
    if (running_t == unix_t && Queue_size != 0){
            addtoQueue(ReadyQ,running_t);
            running_t = removefromQueue(ReadyQ);
            //swapcontext(&current->context,&running_t->context);
    }
    
    swapcontext(&current->context,&running_t->context);   
}

void MyThreadExit(void){

    _MyThread *to_exit = (_MyThread*)malloc(sizeof(_MyThread));
    _MyThread *to_del = (_MyThread*)malloc(sizeof(_MyThread));
    _MyThread *to_run = (_MyThread*)malloc(sizeof(_MyThread));
    _MyThread *par = (_MyThread*)malloc(sizeof(_MyThread));
    
    to_exit = running_t;
    
    //printf("Thread id: %d\n",to_exit->thread_id);

    if (to_exit == unix_t){
        if (Queue_size(ReadyQ) != 0){
            addtoQueue(ReadyQ,to_exit);
            running_t = removefromQueue(ReadyQ);
            swapcontext(&to_exit->context,&running_t->context);
        }
    }
    else
       {    
        if ((to_exit->children)!=NULL){
            while(((to_exit->children)->head)!=NULL){

                (((to_exit->children)->head)->Thread)->parent=NULL;
                ((to_exit->children)->head)=((to_exit->children)->head)->next;
            }
        }

        if(to_exit->parent != NULL){
            if (((to_exit->parent->children)->head)!=NULL){
                to_del = delete_element( to_exit->parent->children, to_exit);
            }
        
            if (to_exit->parent->thread_joinall > 0 && to_exit->joined == 1){
                to_exit->parent->thread_joinall -= 1;
            }
        
            if (to_exit->parent->thread_joinall == 0 && 
                    Queue_element_present(blockedQ,to_exit->parent) == 1)
            {
                par = delete_element(blockedQ, to_exit->parent);
                addtoQueue(ReadyQ, par);
            }
        }

        //printf("Queue size: %d\n",Queue_size(ReadyQ));

        if(Queue_size(ReadyQ)!=0){
            running_t = removefromQueue(ReadyQ);  

            if (running_t == unix_t && Queue_size != 0){
                addtoQueue(ReadyQ,running_t);
                running_t = removefromQueue(ReadyQ);
                //swapcontext(&to_exit->context,&running_t->context);
            }

            swapcontext(&to_exit->context,&running_t->context);
            
        }
        else{    
            //running_t->context = init_context;        
            swapcontext(&to_exit->context,&init_context);
        } 
        
    }
}

/******************************************************************************/

MySemaphore MySemaphoreInit(int initialValue){
    Semaphore *sem;

    sem = (Semaphore*)malloc(sizeof(Semaphore));

    if(sem == NULL){
        printf("Error while allocating memory to semaphore\n");
        return;
    }

    if (initialValue < 0){
        printf("The initial value of semaphore cannot be negative\n");
        return;
    }
    
    sem->initial_value = initialValue;
    sem->curr_value = initialValue;
    sem->SemaphoreQ = (Queue*)malloc(sizeof(Queue));
    Queue_init(sem->SemaphoreQ);

    return (MySemaphore)sem;
}

void MySemaphoreSignal(MySemaphore sem){
    Semaphore *s;
    s = (Semaphore*)malloc(sizeof(Semaphore));

    if(s == NULL){
        printf("SemSignal, Error while allocating memory to semaphore\n");
        return;
    }

    s = (Semaphore*)sem;

    if(s->SemaphoreQ == NULL){
        printf("SemSignal, Semaphore is not active\n");
        return;
    }

    if(s->curr_value < s->initial_value){
        s->curr_value += 1;
    }
    else{
        printf("Semaphore value has reached its limit(initial value). Cannot be incremented further.\n");
        return;
    }
    
    if(s->curr_value <= 0){
        _MyThread *to_Run, *current;

        to_Run = (_MyThread*)malloc(sizeof(_MyThread));
        current = (_MyThread*)malloc(sizeof(_MyThread));
        
        if(to_Run == NULL || current == NULL){
            printf("SemSignal, Error while allocating memory to thread\n");
            return;
        }
        current = running_t;
        
        if(Queue_size(s->SemaphoreQ) != 0){

            to_Run = removefromQueue(s->SemaphoreQ);
            addtoQueue(ReadyQ,to_Run);
            //to_Run = removefromQueue(ReadyQ);
        }
    }
}

void MySemaphoreWait(MySemaphore sem){
    Semaphore *s;
    s = (Semaphore*)malloc(sizeof(Semaphore));

    if(s == NULL){
        printf("SemWait, Error while allocating memory to semaphore\n");
        return;
    }

    s = (Semaphore*)sem;

    if(s->SemaphoreQ == NULL){
        printf("SemWait, Semaphore is not active\n");
        return;
    }

    s->curr_value -= 1;
    
    if(s->curr_value < 0){
        _MyThread *to_Run, *current;

        to_Run = (_MyThread*)malloc(sizeof(_MyThread));
        current = (_MyThread*)malloc(sizeof(_MyThread));
        
        if(to_Run == NULL || current == NULL){
        printf("SemWait, Error while allocating memory to thread\n");
        return;
        }
        current = running_t;
        if(Queue_size(ReadyQ) != 0){
            to_Run = removefromQueue(ReadyQ);
            addtoQueue(s->SemaphoreQ,running_t);
            running_t = to_Run;
            
            if (running_t == unix_t && Queue_size != 0){
                addtoQueue(ReadyQ,running_t);
                running_t = removefromQueue(ReadyQ);
                //swapcontext(&to_exit->context,&running_t->context);
            }
            swapcontext(&current->context,&running_t->context);
        }
        else{
            addtoQueue(s->SemaphoreQ,running_t);
            running_t->context = init_context;
            swapcontext(&current->context,&running_t->context);
        }
    }
}


int MySemaphoreDestroy(MySemaphore sem){
    Semaphore *s;
    s = (Semaphore*)malloc(sizeof(Semaphore));

    if(s == NULL){
        printf("SemWait, Error while allocating memory to semaphore\n");
        return -1;
    }

    s = (Semaphore*)sem;

    if(Queue_size(s->SemaphoreQ) != 0){
        printf("Semaphore cannot be destroyed. Other threads are waiting for semaphore.\n");
        return -1;
    }
    else{
        s->SemaphoreQ = NULL;
        free(s);
        return 0;
    }
}

/* Function to convert Unix process thread into user level thread*/

int MyThreadInitExtra(void){

    if(Thread_count > 0){
        printf("MyThreadInitExtra can be called only once\n");
        return -1;        
    }
    
    exit_context = CreateExitContext();
    
    ReadyQ = (Queue *)malloc(sizeof(Queue));
    blockedQ = (Queue *)malloc(sizeof(Queue));
    Queue_init(ReadyQ);
    Queue_init(blockedQ);
    
    unix_t = (_MyThread *)malloc(sizeof(_MyThread));
       
    getcontext(&unix_t->context);
    //unix_t->context.uc_link = 0;
    unix_t->context.uc_link = &exit_context;
    unix_t->context.uc_stack.ss_sp = malloc(STACK_SIZE);
    unix_t->context.uc_stack.ss_size = STACK_SIZE;
    unix_t->context.uc_stack.ss_flags = 0;
    unix_t->thread_id = Thread_count;
    unix_t->joined = 0;
    unix_t->thread_joinall = 0;
    unix_t->parent = NULL;
    unix_t->children = (Queue *)malloc(sizeof(Queue));
    Queue_init(unix_t->children);    
    running_t = (_MyThread *)malloc(sizeof(_MyThread));
    running_t = unix_t;  
    Thread_count++;  
    
    swapcontext(&running_t->context,&running_t->context);
    
    return 0;
}


void __attribute__ ((destructor))  dtor() { 
  if(unix_t != NULL){
    MyThreadExit(); 
  }
}
