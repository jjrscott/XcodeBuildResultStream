//
//  HelloWorldTests.m
//  HelloWorldTests
//
//  Created by John Scott on 26/02/2021.
//  Copyright © 2021 John Scott. All rights reserved.
//

#import <XCTest/XCTest.h>

@interface HelloWorldTests : XCTestCase

@end

@implementation HelloWorldTests

- (void)setUp {
    // Put setup code here. This method is called before the invocation of each test method in the class.
}

- (void)tearDown {
    // Put teardown code here. This method is called after the invocation of each test method in the class.
}

- (void)testExample {
    // This is an example of a functional test case.
    // Use XCTAssert and related functions to verify your tests produce the correct results.
    XCTFail();
}

- (void)testPerformanceExample {
    // This is an example of a performance test case.
    [self measureBlock:^{
        // Put the code you want to measure the time of here.
    }];
}

@end
